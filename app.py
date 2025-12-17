from flask import Flask, render_template, request, url_for
import random
import math

app = Flask(__name__)

# ==========================================
#  LOGIKA ALGORITMA GENETIKA (HELPER)
# ==========================================
def hitung_ga_knapsack(items_input, capacity, pop_size, generations):
    # 1. Parsing Input dari Text Area
    # Format input: Nama, Berat, Nilai (per baris)
    items = {}
    try:
        lines = items_input.strip().split('\n')
        for line in lines:
            parts = line.split(',')
            name = parts[0].strip()
            weight = int(parts[1].strip())
            value = int(parts[2].strip())
            items[name] = {'weight': weight, 'value': value}
    except Exception as e:
        return None, f"Format data salah: {e}"

    item_list = list(items.keys())
    n_items = len(item_list)
    
    # Logika GA Helper
    def decode(chromosome):
        total_weight = 0
        total_value = 0
        chosen_items = []
        for gene, name in zip(chromosome, item_list):
            if gene == 1:
                total_weight += items[name]['weight']
                total_value += items[name]['value']
                chosen_items.append(name)
        return chosen_items, total_weight, total_value

    def fitness(chromosome):
        _, w, v = decode(chromosome)
        return v if w <= capacity else 0

    # Inisialisasi Populasi
    population = [[random.randint(0, 1) for _ in range(n_items)] for _ in range(pop_size)]
    
    logs = [] # Untuk menyimpan riwayat evolusi

    # Loop Generasi
    for gen in range(generations):
        fitnesses = [fitness(ch) for ch in population]
        
        # Elitism (Simpan yang terbaik)
        best_idx = fitnesses.index(max(fitnesses))
        best_chrom = population[best_idx][:]
        
        # Catat log setiap beberapa generasi (atau awal dan akhir)
        if gen == 0 or gen == generations - 1:
            items_chosen, w, v = decode(best_chrom)
            logs.append({
                'gen': gen + 1,
                'list_barang': ", ".join(items_chosen),  
                'weight': w,
                'value': v
            })

        # Seleksi & Reproduksi (Sederhana)
        new_pop = [best_chrom] # Elitism
        while len(new_pop) < pop_size:
            # Tournament Selection sederhana
            p1 = random.choice(population)
            p2 = random.choice(population)
            
            # Crossover (Single Point)
            cut = random.randint(1, n_items - 1) if n_items > 1 else 0
            child = p1[:cut] + p2[cut:]
            
            # Mutasi
            if random.random() < 0.1: # Rate mutasi 10%
                mutation_point = random.randint(0, n_items - 1)
                child[mutation_point] = 1 - child[mutation_point]
            
            new_pop.append(child)
        
        population = new_pop

    # Hasil Akhir
    final_fitnesses = [fitness(ch) for ch in population]
    best_idx = final_fitnesses.index(max(final_fitnesses))
    best_chrom = population[best_idx]
    best_items, best_w, best_v = decode(best_chrom)

    result = {
        'best_items': best_items,
        'total_weight': best_w,
        'total_value': best_v,
        'capacity': capacity,
        'logs': logs
    }
    return result, None

# ==========================================
#  LOGIKA TSP (HELPER FUNCTIONS)
# ==========================================

def hitung_jarak(kota1, kota2):
    """Menghitung jarak Euclidean antar 2 titik koordinat"""
    return math.sqrt((kota1[0] - kota2[0])**2 + (kota1[1] - kota2[1])**2)

def hitung_total_jarak(rute, koordinat_kota):
    """Menghitung total jarak satu putaran penuh"""
    jarak = 0
    jumlah_kota = len(rute)
    for i in range(jumlah_kota):
        idx_sekarang = rute[i]
        idx_berikutnya = rute[(i + 1) % jumlah_kota] # % agar kembali ke awal
        
        k1 = koordinat_kota[idx_sekarang]
        k2 = koordinat_kota[idx_berikutnya]
        jarak += hitung_jarak(k1, k2)
    return jarak

def solve_tsp_ga(jumlah_kota, generations):
    """Fungsi utama Algoritma Genetika untuk TSP"""
    
    # 1. Generate Koordinat Kota secara Acak (Area 500x300 pixel)
    koordinat_kota = []
    for _ in range(jumlah_kota):
        x = random.randint(20, 480)
        y = random.randint(20, 280)
        koordinat_kota.append((x, y))
    
    # 2. Inisialisasi Populasi (Rute Acak)
    pop_size = 60
    population = []
    base_route = list(range(jumlah_kota)) # [0, 1, 2, ... N-1]
    
    for _ in range(pop_size):
        rute_baru = base_route[:]
        random.shuffle(rute_baru)
        population.append(rute_baru)

    best_route_global = None
    min_dist_global = float('inf')

    # 3. Loop Evolusi
    for gen in range(generations):
        # Hitung skor setiap rute
        scores = []
        for rute in population:
            d = hitung_total_jarak(rute, koordinat_kota)
            scores.append((d, rute))
            
            # Cek apakah ini rekor terbaik sejauh ini
            if d < min_dist_global:
                min_dist_global = d
                best_route_global = rute[:]
        
        # Urutkan populasi (Jarak terpendek di atas)
        scores.sort(key=lambda x: x[0])
        sorted_pop = [x[1] for x in scores]
        
        # Seleksi: Ambil 50% terbaik sebagai orang tua
        parents = sorted_pop[:pop_size//2]
        
        # Reproduksi untuk mengisi populasi baru
        new_pop = parents[:] 
        
        while len(new_pop) < pop_size:
            # Pilih 2 orang tua acak dari daftar terbaik
            p1 = random.choice(parents)
            p2 = random.choice(parents)
            
            # Crossover (Ordered Crossover)
            # Tujuannya: Menggabungkan rute tanpa duplikasi kota
            start, end = sorted(random.sample(range(jumlah_kota), 2))
            child = [-1] * jumlah_kota
            
            # Salin sebagian gen dari P1
            child[start:end] = p1[start:end]
            
            # Isi sisanya dengan urutan dari P2 (yang belum ada di child)
            pointer = 0
            for gene in p2:
                if gene not in child:
                    # Cari slot kosong (-1) berikutnya
                    while child[pointer] != -1:
                        pointer += 1
                    child[pointer] = gene
            
            # Mutasi (Swap Mutation)
            # Tukar posisi 2 kota secara acak (peluang 20%)
            if random.random() < 0.2:
                idx1, idx2 = random.sample(range(jumlah_kota), 2)
                child[idx1], child[idx2] = child[idx2], child[idx1]
            
            new_pop.append(child)
        
        population = new_pop

    # Kembalikan hasil untuk ditampilkan di HTML
    return {
        'koordinat': koordinat_kota, # Posisi X,Y kota
        'best_route': best_route_global, # Urutan kunjungan [0, 5, 2...]
        'jarak': round(min_dist_global, 2)
    }

# ==========================================
#  ROUTES FLASK
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tugas/<int:nomor_tugas>', methods=['GET', 'POST'])
def tampilkan_tugas(nomor_tugas):
    if nomor_tugas == 1:
        return render_template('tugas1.html')
    
    elif nomor_tugas == 2:
        hasil = None
        error = None
        
        # Default values untuk form
        default_items = "Laptop, 7, 5\nBuku, 2, 4\nBotol Air, 1, 7\nKamera, 9, 2"
        default_capacity = 15
        
        if request.method == 'POST':
            # Ambil data dari form HTML
            items_input = request.form.get('items_input')
            capacity_input = int(request.form.get('capacity'))
            generations_input = int(request.form.get('generations', 10))
            
            # Jalankan GA
            hasil, error = hitung_ga_knapsack(items_input, capacity_input, 10, generations_input)
            
            # Agar form tetap terisi data terakhir
            default_items = items_input
            default_capacity = capacity_input

        return render_template('tugas2.html', 
                             hasil=hasil, 
                             error=error, 
                             default_items=default_items, 
                             default_capacity=default_capacity)

    elif nomor_tugas == 3:
        hasil = None
        # Default value
        default_kota = 15 
        default_gen = 100
        
        if request.method == 'POST':
            # Ambil input dinamis dari user
            default_kota = int(request.form.get('jumlah_kota'))
            default_gen = int(request.form.get('generations'))
            
            # Jalankan Algoritma
            hasil = solve_tsp_ga(default_kota, default_gen)
            
        return render_template('tugas3.html', 
                               hasil=hasil, 
                               default_kota=default_kota, 
                               default_gen=default_gen)

if __name__ == '__main__':
    app.run(debug=True)