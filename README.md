# Air Pollution Interactive Dashboard

Proyek ini merupakan **dashboard interaktif** untuk menganalisis data polusi udara. Data yang digunakan terdiri dari beberapa file CSV berisi informasi konsentrasi polutan (PM2.5, PM10, SO2, NO2, CO, O3) serta variabel cuaca (TEMP, WSPM, dll.). Dashboard dibangun menggunakan **[Streamlit](https://streamlit.io/)**, sehingga mudah diakses dan dipahami oleh berbagai kalangan.

## Table of Contents

1. [Fitur Utama](#fitur-utama)  
2. [Struktur Folder](#struktur-folder)  
3. [Persyaratan (Requirements)](#persyaratan-requirements)  
4. [Cara Menjalankan di Lokal](#cara-menjalankan-di-lokal)  
5. [Panduan Penggunaan](#panduan-penggunaan)  
6. [Kontak dan Kontribusi](#kontak-dan-kontribusi)

---

## Fitur Utama

- **Load Data**: Memuat semua file CSV dari folder tertentu, lalu menggabungkannya menjadi satu *DataFrame*.
- **Ringkasan Statistik**: Menampilkan deskriptif statistik dari berbagai kolom numerik serta jumlah *missing values*.
- **EDA**:  
  - **Histogram & Boxplot**: Memvisualisasikan distribusi dan outliers dari polutan/cuaca.  
  - **Heatmap Korelasi**: Untuk melihat hubungan antarvariabel polutan dan faktor cuaca.
- **Analisis Tren**:  
  - Agregasi polutan per tahun.  
  - Kalkulasi *slope* (linregress) untuk memantau pergerakan polutan di tiap stasiun per tahun.  
  - Visualisasi *line chart* per tahun.
- **Peta Interaktif**:  
  - Menggunakan **Folium** untuk menampilkan stasiun beserta polutan (marker dan heatmap).  
  - Memudahkan identifikasi area-area dengan polutan tinggi.

---

## Struktur Folder

Berikut contoh struktur folder minimal:

```
my_project/
│
├── dashboard.py               # File utama berisi kode Streamlit
├── README.md                  # Dokumentasi proyek
├── requirements.txt           # Daftar library yang dibutuhkan
└── data/                      # Folder berisi file-file CSV
    ├── main_data.csv
    └── ...
```

> **Catatan**:  
> - Pastikan `dashboard.py` dan folder `data` berada dalam 1 project, agar mudah mengakses data menggunakan relative path.  
> - Jika Anda memiliki banyak file CSV, semuanya bisa diletakkan di folder `data`.

---

## Persyaratan (Requirements)

Untuk menjalankan proyek ini, Anda membutuhkan beberapa library Python. Seluruh kebutuhan tercantum pada **`requirements.txt`**. Contoh:

```txt
folium==0.14.0
geopandas==0.12.2
matplotlib==3.6.2
missingno==0.5.1
numpy==1.23.5
pandas==1.5.3
plotly==5.11.0
scipy==1.10.0
seaborn==0.12.2
statsmodels==0.13.5
streamlit==1.17.0
streamlit-folium==0.9.2
```

---

## Cara Menjalankan di Lokal

1. **Clone Repository**  
   Unduh atau cloning repositori ini:
   ```bash
   git clone <URL-REPO-ANDA>
   cd my_project
   ```

2. **Buat Virtual Environment (Opsional tapi Disarankan)**  
   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux/Mac
   # atau
   venv\Scripts\activate        # Windows
   ```

3. **Instal Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Struktur Folder Data**  
   Pastikan file CSV Anda berada di folder `data/` atau sesuaikan path folder di sidebar nanti.

5. **Jalankan Streamlit**  
   ```bash
   streamlit run dashboard.py
   ```
   Perintah tersebut akan membuka browser secara otomatis di `http://localhost:8501`.

---

## Panduan Penggunaan

1. **Sidebar** – Terdapat beberapa *widget*:  
   - **Folder Data CSV**: Masukkan path folder tempat file CSV disimpan (default: `data`).  
   - **Load Data**: Klik untuk memuat dan menggabungkan seluruh file CSV.  
2. **Tab “Overview”** – Menampilkan ringkasan statistik dan informasi *missing values*.  
3. **Tab “Exploratory Data Analysis”**  
   - Pilih kolom numerik & tipe plot untuk melihat distribusinya (Histogram/Boxplot).  
   - Opsi “Tampilkan Korelasi Heatmap” untuk meninjau korelasi antarvariabel numerik.  
4. **Tab “Tren Per Tahun & Stasiun”**  
   - Menampilkan tren polutan per tahun (line chart).  
   - Perhitungan *slope* (linregress) tiap stasiun untuk melihat polutan yang meningkat/menurun.  
5. **Tab “Visualisasi Peta”**  
   - Multiselect polutan yang ingin di-*overlay* di peta.  
   - Terdapat dua layer: Marker dan Heatmap. *Marker* dapat diklik untuk info detail. *Heatmap* membantu melihat konsentrasi area polutan tertinggi.

---

## Kontak dan Kontribusi

- **Laporkan Masalah**: Jika menemukan *bug*, silakan buka [Issues](#).  
- **Kontribusi**: Ajukan pull request untuk perbaikan atau penambahan fitur.  
- **Email**: hubungi `hmazka19@gmail.com` jika ada pertanyaan lebih lanjut.

> Terima kasih sudah menggunakan **Air Pollution Interactive Dashboard**! Semoga bermanfaat dan memudahkan Anda dalam menganalisis data polusi udara. Jangan ragu melakukan kontribusi, saran, atau perbaikan!
