import streamlit as st
import cadquery as cq
import plotly.graph_objects as go
import tempfile
import os
import numpy as np

# 1. KONFIGURASI HALAMAN UTAMA & TEMA PREMIUM NEON CAM
st.set_page_config(
    page_title="AI-CAM Engine v8.5 - 1:1 Synced Viewport",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kustomisasi Style Antarmuka Gelap (Industrial Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0a0a0a; color: #ecf0f1; }
    .sidebar .sidebar-content { background-color: #111418; }
    h1, h2, h3 { font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: PARAMETER INPUT & SETUP PAHAT ---
st.sidebar.title("⚙️ AI-CAM Engine v8.5")
st.sidebar.markdown("**Parameter & Setup Pahat**")
st.sidebar.markdown("---")

st.sidebar.subheader("📦 SETUP RAW MATERIAL (STOCK)")
margin_x = st.sidebar.number_input("Margin Kiri/Kanan X (mm)", value=5.0, step=1.0)
margin_y = st.sidebar.number_input("Margin Depan/Belakang Y (mm)", value=5.0, step=1.0)
margin_z_atas = st.sidebar.number_input("Margin Facing Atas Z (mm)", value=2.0, step=0.5)
margin_z_bawah = st.sidebar.number_input("Margin Support Bawah Z (mm)", value=0.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ SETTING GERAKAN CUTTING")
jarak_aman = st.sidebar.number_input("Z Clearance / Retract Safe (mm)", value=10.0, step=1.0)
feed_rate_cutting = st.sidebar.number_input("Kecepatan Potong (F mm/min)", value=800, step=50)

# --- HALAMAN UTAMA ---
st.markdown("<h1 style='color: #007acc; margin-bottom: 0;'>⚙️ HIGH-RESOLUTION 1:1 TOOLPATH VIEWPORT</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #bdc3c7; font-style: italic;'>Garis Jalur Pahat Terkunci Presisi Secara Matematis dengan Output G-code.</p>", unsafe_allow_html=True)
st.markdown("---")

uploaded_file = st.file_uploader("📂 UNGGAH FILE CAD MODEL (.STP / .STEP)", type=["stp", "step"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stp") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        # Import file CAD
        benda_kerja = cq.importers.importStep(tmp_path)
        faces = benda_kerja.faces().vals()
        bbox = benda_kerja.val().BoundingBox()
        
        # Kalkulasi Stock Batas Luar Material Mentah
        stock_xmin = float(bbox.xmin) - margin_x
        stock_xmax = float(bbox.xmax) + margin_x
        stock_ymin = float(bbox.ymin) - margin_y
        stock_ymax = float(bbox.ymax) + margin_y
        stock_zmin = float(bbox.zmin) - margin_z_bawah
        stock_zmax = float(bbox.zmax) + margin_z_atas

        # --- 1. SCANNING GEOMETRI CAD (FIXED ERROR 'CENTER') ---
        info_lubang = []      

        for f in faces:
            geom_type = str(f.geomType()).upper()
            f_bbox = f.BoundingBox()
            
            # Perbaikan kalkulasi Titik Tengah manual agar bebas crash
            cx = (f_bbox.xmin + f_bbox.xmax) / 2.0
            cy = (f_bbox.ymin + f_bbox.ymax) / 2.0
            
            if "CYLINDER" in geom_type:
                dia = round(min(f_bbox.xlen, f_bbox.ylen), 2)
                if dia > 0:
                    pos = (round(cx, 2), round(cy, 2))
                    if pos not in [l[0] for l in info_lubang]:
                        info_lubang.append((pos, float(f_bbox.zmin)))

        # --- 2. GENERATOR JALUR UTAMA (SINGLE SOURCE OF TRUTH) ---
        plot_data = {
            'Facing': {'x': [], 'y': [], 'z': []},
            'Roughing': {'x': [], 'y': [], 'z': []},
            'Drilling': {'x': [], 'y': [], 'z': []},
            'Rapid': {'x': [], 'y': [], 'z': []}
        }

        gcode = [
            "(=== AI-CAM HIGH-RES PRECISION G-CODE ===)",
            "(--- HARMONIZED 1:1 WITH PLOTTER LINES ---)",
            "G21 (Unit: mm)", "G90 (Absolute)", "G17 (XY Plane Select)",
            f"G00 Z{stock_zmax + jarak_aman:.4f} (Rapid Safe Altitude)"
        ]

        curr_x, curr_y, curr_z = 0.0, 0.0, stock_zmax + jarak_aman

        # A. PROSES OP 1: FACING (Garis Hijau Neon)
        gcode.append("\n(--- OP 1: FACING OPERATION ---)\nT01 M06\nM03 S3000 M08")
        y_steps = np.linspace(stock_ymin, stock_ymax, 6)
        for i, y_pos in enumerate(y_steps):
            start_x = stock_xmin if i % 2 == 0 else stock_xmax
            target_x = stock_xmax if i % 2 == 0 else stock_xmin
            
            gcode.append(f"G00 X{start_x:.4f} Y{y_pos:.4f} Z{stock_zmax:.4f}")
            plot_data['Rapid']['x'].extend([curr_x, start_x, None]); plot_data['Rapid']['y'].extend([curr_y, y_pos, None]); plot_data['Rapid']['z'].extend([curr_z, stock_zmax, None])
            
            gcode.append(f"G01 X{target_x:.4f} Y{y_pos:.4f} F{feed_rate_cutting:.0f}")
            plot_data['Facing']['x'].extend([start_x, target_x, None]); plot_data['Facing']['y'].extend([y_pos, y_pos, None]); plot_data['Facing']['z'].extend([stock_zmax, stock_zmax, None])
            curr_x, curr_y, curr_z = target_x, y_pos, stock_zmax

        gcode.append(f"G00 Z{stock_zmax + jarak_aman:.4f}")
        plot_data['Rapid']['x'].extend([curr_x, curr_x, None]); plot_data['Rapid']['y'].extend([curr_y, curr_y, None]); plot_data['Rapid']['z'].extend([curr_z, stock_zmax + jarak_aman, None])
        curr_z = stock_zmax + jarak_aman

        # B. PROSES OP 2: POCKETING / ROUGHING STEP (Garis Cyan Neon)
        gcode.append("\n(--- OP 2: POCKETING ROUGHING ---)\nT02 M06\nM03 S4500 M08")
        z_rough_levels = [stock_zmax - (stock_zmax - float(bbox.zmin)) * 0.5, float(bbox.zmin)]
        offsets = [0.8, 0.6, 0.4, 0.2]
        
        for z_lvl in z_rough_levels:
            for f_off in offsets:
                rx_min = float(bbox.xmin) + (float(bbox.xmax) - float(bbox.xmin)) * (1 - f_off) / 2
                rx_max = float(bbox.xmax) - (float(bbox.xmax) - float(bbox.xmin)) * (1 - f_off) / 2
                ry_min = float(bbox.ymin) + (float(bbox.ymax) - float(bbox.ymin)) * (1 - f_off) / 2
                ry_max = float(bbox.ymax) - (float(bbox.ymax) - float(bbox.ymin)) * (1 - f_off) / 2
                
                gcode.append(f"G00 X{rx_min:.4f} Y{ry_min:.4f}")
                plot_data['Rapid']['x'].extend([curr_x, rx_min, None]); plot_data['Rapid']['y'].extend([curr_y, ry_min, None]); plot_data['Rapid']['z'].extend([curr_z, z_lvl, None])
                
                gcode.extend([f"G01 Z{z_lvl:.4f} F250", f"G01 X{rx_max:.4f} Y{ry_min:.4f} F{feed_rate_cutting:.0f}", f"G01 X{rx_max:.4f} Y{ry_max:.4f}", f"G01 X{rx_min:.4f} Y{ry_max:.4f}", f"G01 X{rx_min:.4f} Y{ry_min:.4f}"])
                plot_data['Roughing']['x'].extend([rx_min, rx_max, rx_max, rx_min, rx_min, None])
                plot_data['Roughing']['y'].extend([ry_min, ry_min, ry_max, ry_max, ry_min, None])
                plot_data['Roughing']['z'].extend([z_lvl, z_lvl, z_lvl, z_lvl, z_lvl, None])
                curr_x, curr_y, curr_z = rx_min, ry_min, z_lvl

        gcode.append(f"G00 Z{stock_zmax + jarak_aman:.4f}")
        plot_data['Rapid']['x'].extend([curr_x, curr_x, None]); plot_data['Rapid']['y'].extend([curr_y, curr_y, None]); plot_data['Rapid']['z'].extend([curr_z, stock_zmax + jarak_aman, None])
        curr_z = stock_zmax + jarak_aman

        # C. PROSES OP 3: DRILLING CYCLE (Garis Merah)
        if info_lubang:
            gcode.append("\n(--- OP 3: DRILLING CYCLE ---)\nT03 M06\nM03 S2200 M08")
            for pos, z_hole_bottom in info_lubang:
                hx, hy = pos
                gcode.extend([f"G00 X{hx:.4f} Y{hy:.4f}", f"G00 Z{stock_zmax + 2.0:.4f}", f"G83 X{hx:.4f} Y{hy:.4f} Z{z_hole_bottom:.4f} R{stock_zmax+2.0:.4f} Q2.0 F120", "G80", f"G00 Z{stock_zmax + jarak_aman:.4f}"])
                plot_data['Rapid']['x'].extend([curr_x, hx, hx, None]); plot_data['Rapid']['y'].extend([curr_y, hy, hy, None]); plot_data['Rapid']['z'].extend([curr_z, curr_z, stock_zmax + 2.0, None])
                plot_data['Drilling']['x'].extend([hx, hx, None]); plot_data['Drilling']['y'].extend([hy, hy, None]); plot_data['Drilling']['z'].extend([stock_zmax + 2.0, z_hole_bottom, None])
                curr_x, curr_y, curr_z = hx, hy, stock_zmax + jarak_aman

        gcode.append("\nM30 (End of Program)")
        gcode_text = "\n".join(gcode)

        # --- 3. PEMBUATAN LAYOUT VIEWPORT SEJAJAR ---
        st.success("Refreshed! Sinkronisasi Tema Premium Neon Berhasil Aktif.")
        col1, col2 = st.columns([6, 4])

        with col1:
            st.markdown("### 🖥️ HIGH-RES NEON VIEWPORT")
            fig = go.Figure()

            # Menggambar Kotak Transparan Material Mentah (Stock)
            fig.add_trace(go.Mesh3d(
                x=[stock_xmin, stock_xmax, stock_xmax, stock_xmin, stock_xmin, stock_xmax, stock_xmax, stock_xmin],
                y=[stock_ymin, stock_ymin, stock_ymax, stock_ymax, stock_ymin, stock_ymin, stock_ymax, stock_ymax],
                z=[stock_zmax, stock_zmax, stock_zmax, stock_zmax, stock_zmin, stock_zmin, stock_zmin, stock_zmin],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                opacity=0.03, color="white", name="Raw Stock Block"
            ))

            # Menggambar Model Solid Benda Kerja CAD
            try:
                vertices, triangles = benda_kerja.val().tessellate(0.4)
                fig.add_trace(go.Mesh3d(
                    x=[v.x for v in vertices], y=[v.y for v in vertices], z=[v.z for v in vertices],
                    i=[t[0] for t in triangles], j=[t[1] for t in triangles], k=[t[2] for t in triangles],
                    color='#1e272e', opacity=0.6, name="CAD Solid Model"
                ))
            except: pass

            # Menampilkan Garis Jalur Pahat Terpilih
            if plot_data['Rapid']['x']: fig.add_trace(go.Scatter3d(x=plot_data['Rapid']['x'], y=plot_data['Rapid']['y'], z=plot_data['Rapid']['z'], mode='lines', line=dict(color='yellow', width=1.5, dash='dash'), name='Rapid Move (G00)'))
            if plot_data['Facing']['x']: fig.add_trace(go.Scatter3d(x=plot_data['Facing']['x'], y=plot_data['Facing']['y'], z=plot_data['Facing']['z'], mode='lines', line=dict(color='#00ff88', width=3.5), name='Facing Pass (T01)'))
            if plot_data['Roughing']['x']: fig.add_trace(go.Scatter3d(x=plot_data['Roughing']['x'], y=plot_data['Roughing']['y'], z=plot_data['Roughing']['z'], mode='lines', line=dict(color='#00ffff', width=3.5), name='Pocket/Roughing (T02)'))
            if plot_data['Drilling']['x']: fig.add_trace(go.Scatter3d(x=plot_data['Drilling']['x'], y=plot_data['Drilling']['y'], z=plot_data['Drilling']['z'], mode='lines+markers', line=dict(color='#ff3838', width=4), marker=dict(size=5, color='white'), name='Drilling Cycle (T03)'))

            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                scene=dict(
                    bgcolor="#0a0a0a", aspectmode='data',
                    xaxis=dict(gridcolor='#222', title='X (mm)'),
                    yaxis=dict(gridcolor='#222', title='Y (mm)'),
                    zaxis=dict(gridcolor='#222', title='Z (mm)')
                ),
                margin=dict(l=0, r=0, b=0, t=0), height=700
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📄 DIRECT G-CODE TEXT")
            st.text_area("G-Code Symmetrical Output Preview", value=gcode_text, height=540)
            st.download_button("📥 DOWNLOAD PRECISION .NC FILE", data=gcode_text, file_name="ai_cam_output.nc")

    except Exception as e:
        st.error(f"Sistem Gagal Memproses File CAD: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
