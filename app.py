from flask import Flask, render_template

app = Flask(__name__)

# Rute 1: Halaman Utama (Menu)
@app.route('/')
def index():
    # Halaman ini hanya akan menampilkan pesan selamat datang
    # Menunya sendiri ada di layout.html
    return render_template('index.html')

# Rute 2: Halaman Tugas (menggunakan rute dinamis)
@app.route('/tugas/<int:nomor_tugas>')
def tampilkan_tugas(nomor_tugas):
    if nomor_tugas == 1:
        # Jika URL-nya /tugas/1, tampilkan file tugas1.html
        return render_template('tugas1.html')
    elif 2 <= nomor_tugas <= 7:
        # Jika /tugas/2 sampai /tugas/7, tampilkan placeholder
        # Kita kirim 'nomor' agar template tahu tugas ke berapa
        return render_template('tugas_placeholder.html', nomor=nomor_tugas)
    else:
        # Jika nomor tugas tidak valid (misal /tugas/9)
        return "Tugas tidak ditemukan", 404

if __name__ == '__main__':
    app.run(debug=True)