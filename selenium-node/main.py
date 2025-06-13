import multiprocessing
from script import batik, lion, saj, pelita

def run_batik():
    batik.main_batik()

def run_lion():
    lion.main_lion()

def run_saj():
    saj.main_saj()

def run_pelita():
    pelita.main_pelita()

if __name__ == "__main__":
    # Membuat dan menjalankan proses secara paralel
    processes = []

    # Menambahkan setiap proses
    processes.append(multiprocessing.Process(target=run_batik))
    processes.append(multiprocessing.Process(target=run_lion))
    processes.append(multiprocessing.Process(target=run_saj))
    processes.append(multiprocessing.Process(target=run_pelita))

    # Memulai semua proses
    for p in processes:
        p.start()

    # Menunggu semua proses selesai
    for p in processes:
        p.join()

    print("Semua skrip telah selesai dijalankan.")
