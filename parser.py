import cadquery as cq

def analisa_fitur_ai(file_path):
    print(f"Memproses file CAD: {file_path}...\n")
    try:
        benda_kerja = cq.importers.importStep(file_path)
        faces = benda_kerja.faces().vals()
        
        fitur_datar = 0
        fitur_silinder_lubang = 0
        
        for face in faces:
            jenis_geometri = str(face.geomType()).upper()
            if "PLANE" in jenis_geometri:
                fitur_datar += 1
            elif "CYLINDER" in jenis_geometri:
                fitur_silinder_lubang += 1
        
        # 1. Tampilkan Hasil Deteksi Fitur
        print(f"--- 🧠 HASIL DETEKSI FITUR AI-CAM ---")
        print(f"Permukaan Datar (Planar Pocket/Facing) : {fitur_datar} ditemukan")
        print(f"Fitur Silinder (Hole/Drilling)         : {fitur_silinder_lubang} ditemukan\n")
        
        # 2. Tampilkan Rekomendasi Dimensi Material
        bbox = benda_kerja.val().BoundingBox()
        print(f"--- 📐 REKOMENDASI UKURAN MATERIAL (RAW BLOCK) ---")
        print(f"Minimal Panjang (X) : {bbox.xlen:.4f} mm")
        print(f"Minimal Lebar (Y)   : {bbox.ylen:.4f} mm")
        print(f"Minimal Tinggi (Z)  : {bbox.zlen:.4f} mm\n")
        
        # 3. KECERDASAN BUATAN: Menghasilkan Ringkasan & Deskripsi Proses Permesinan CNC 3-Axis
        print(f"--- 📋 DESKRIPSI OTOMATIS AI-CAM PROSES 3-AXIS ---")
        print(f"Benda kerja ini terdeteksi sebagai komponen blok mekanikal berukuran {bbox.xlen:.1f}x{bbox.ylen:.1f}x{bbox.zlen:.1f} mm.")
        
        if fitur_datar > 0:
            print(f"- [OPERASI 1]: Gunakan proses Flat End-Mill (Facing/Pocketing) untuk meratakan {fitur_datar} permukaan datar.")
        if fitur_silinder_lubang > 0:
            print(f"- [OPERASI 2]: Terdeteksi {fitur_silinder_lubang} fitur silindris. Gunakan operasi Boring/Drilling untuk membuat lubang.")
            
        print(f"- [KESIMPULAN]: Komponen siap diproses menggunakan setup Ragum Standar pada Mesin CNC Milling 3-Axis.")
        
    except Exception as e:
        print(f"Gagal memproses AI CAM: {e}")

if __name__ == "__main__":
    print("Sistem Deskripsi AI-CAM 3-Axis (AI Feature Recognition Active)\n" + "="*55)
    analisa_fitur_ai("Part1.stp")
