import cadquery as cq

def analisa_fitur_ai(file_path):
    print(f"Memproses file CAD: {file_path}...\n")
    try:
        benda_kerja = cq.importers.importStep(file_path)
        faces = benda_kerja.faces().vals()
        
        fitur_datar = 0
        fitur_silinder_lubang = 0
        
        # AI menganalisis satu per satu permukaan objek
        for face in faces:
            jenis_geometri = face.GeometryType()
            
            # Aturan AI 1: Jika permukaan datar, ini area potensial untuk Facing/Pocketing CNC
            if jenis_geometri == "PLANE":
                fitur_datar += 1
            # Aturan AI 2: Jika berbentuk silinder, ini adalah lubang/poros untuk Drilling
            elif jenis_geometri == "CYLINDER":
                fitur_silinder_lubang += 1
        
        # Menampilkan Ringkasan Analisis AI
        print(f"--- 🧠 HASIL DETEKSI FITUR AI-CAM ---")
        print(f"Permukaan Datar (Planar Pocket/Facing) : {fitur_datar} ditemukan")
        print(f"Fitur Silinder (Hole/Drilling)         : {fitur_silinder_lubang} ditemukan\n")
        
        # Ekstraksi Bounding Box untuk Ukuran Raw Material
        bbox = benda_kerja.val().BoundingBox()
        print(f"--- 📐 REKOMENDASI UKURAN MATERIAL (RAW BLOCK) ---")
        print(f"Minimal Panjang (X) : {bbox.xlen:.4f} mm")
        print(f"Minimal Lebar (Y)   : {bbox.ylen:.4f} mm")
        print(f"Minimal Tinggi (Z)  : {bbox.zlen:.4f} mm")
        
    except Exception as e:
        print(f"Gagal memproses AI CAM: {e}")

if __name__ == "__main__":
    print("Sistem Deskripsi AI-CAM 3-Axis (AI Feature Recognition Active)\n" + "="*55)
    analisa_fitur_ai("Part1.stp")
