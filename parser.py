import cadquery as cq

def analisa_file_step(file_path):
    print(f"Memproses file CAD: {file_path}...\n")
    
    try:
        # Memuat file STEP menggunakan mesin OpenCASCADE
        benda_kerja = cq.importers.importStep(file_path)
        
        # Mengekstrak fitur geometri dasar
        faces = benda_kerja.faces().vals()
        edges = benda_kerja.edges().vals()
        vertices = benda_kerja.vertices().vals()
        
        print(f"--- Hasil Ekstraksi Geometri ---")
        print(f"Total Permukaan (Faces) : {len(faces)}")
        print(f"Total Tepi (Edges)      : {len(edges)}")
        print(f"Total Titik (Vertices)  : {len(vertices)}\n")
        
        # Mendapatkan dimensi absolut (Bounding Box)
        # Di sinilah kita membuktikan toleransi presisi tinggi
        bbox = benda_kerja.val().BoundingBox()
        print(f"--- Dimensi Benda Kerja ---")
        print(f"Panjang (X) : {bbox.xlen:.4f} mm")
        print(f"Lebar (Y)   : {bbox.ylen:.4f} mm")
        print(f"Tinggi (Z)  : {bbox.zlen:.4f} mm")
        
    except Exception as e:
        print(f"Gagal membaca file STEP: {e}")

if __name__ == "__main__":
    print("Sistem Parser AI-CAM 3-Axis (Engine Ready)\n" + "="*40)
    
    # Untuk mengujinya, hapus tanda pagar (#) pada baris di bawah 
    # dan pastikan Anda memiliki file 'contoh_part.step' di folder yang sama
    # analisa_file_step("contoh_part.step")
