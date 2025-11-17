from flask import Flask, render_template, request, url_for
import random

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

    elif 3 <= nomor_tugas <= 7:
        return render_template('tugas_placeholder.html', nomor=nomor_tugas)
    else:
        return "Tugas tidak ditemukan", 404

if __name__ == '__main__':
    app.run(debug=True)