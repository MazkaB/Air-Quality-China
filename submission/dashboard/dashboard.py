# dashboard.py

import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

# Untuk Folium di Streamlit (opsional)

from streamlit_folium import st_folium
import folium
from folium.plugins import Fullscreen, MeasureControl, MiniMap, HeatMap

import warnings
warnings.filterwarnings('ignore')

##########################
# 1. BAGIAN FUNGSI-FUNGSI
##########################

@st.cache_data
def load_data(data_folder: str, columns_to_check=None):
    """
    Memuat semua CSV dari folder data_folder,
    lalu menggabungkannya menjadi satu DataFrame.
    Mengembalikan DataFrame gabungan dengan kolom timestamp.
    """
    if columns_to_check is None:
        columns_to_check = ['year', 'month', 'day', 'hour']
    
    # List untuk menampung semua DataFrame
    all_data = []
    
    # Loop setiap file CSV dalam folder
    for filename in os.listdir(data_folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(data_folder, filename)
            df = pd.read_csv(filepath)
            all_data.append(df)
    
    # Gabungkan semua DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Pastikan kolom time tersedia
    if all(col in combined_df.columns for col in columns_to_check):
        combined_df['timestamp'] = pd.to_datetime(combined_df[columns_to_check])
        combined_df.drop(columns=columns_to_check, inplace=True)
    else:
        st.warning("Tidak semua kolom (year, month, day, hour) ditemukan. Timestamp mungkin tidak akurat.")
    
    return combined_df


def create_folium_map(df, pollutants):
    """
    Membuat Folium Map yang menampilkan marker dan heatmap untuk
    polutan yang dipilih, berdasarkan rata-rata per stasiun.
    Pastikan df memiliki kolom: ['station', pollutant, 'lat', 'lon'].
    """
    # Dictionary koordinat stasiun (latitude, longitude)
    station_coords = {
        "Aotizhongxin": (39.917, 116.397),
        "Changping": (40.218, 116.231),
        "Dingling": (40.091, 116.316),
        "Dongsi": (39.935, 116.419),
        "Guanyuan": (39.941, 116.391),
        "Gucheng": (40.107, 116.261),
        "Huairou": (40.337, 116.640),
        "Nongzhanguan": (39.932, 116.360),
        "Shunyi": (40.127, 116.653),
        "Tiantan": (39.883, 116.403),
        "Wanliu": (39.979, 116.307),
        "Wanshouxigong": (39.936, 116.332)
    }
    
    # Warna marker per polutan
    colors = {
        'PM2.5': 'red',
        'PM10': 'orange',
        'SO2': 'purple',
        'NO2': 'darkred',
        'CO': 'black',
        'O3': 'green'
    }
    
    # Faktor skala agar marker kelihatan berbeda ukurannya
    scaling = {
        'PM2.5': 0.1,
        'PM10': 0.05,
        'SO2': 1,
        'NO2': 1,
        'CO': 0.005,
        'O3': 1
    }
    
    # Siapkan map
    base_map = folium.Map(location=[39.9, 116.4], zoom_start=10, tiles="OpenStreetMap")
    Fullscreen().add_to(base_map)
    MeasureControl().add_to(base_map)
    MiniMap().add_to(base_map)
    
    # Hitung rata-rata polutan per stasiun
    for pollutant in pollutants:
        if pollutant not in df.columns:
            continue
        
        df_poll = df.groupby('station')[[pollutant]].mean().reset_index()
        df_poll['lat'] = df_poll['station'].apply(lambda x: station_coords[x][0])
        df_poll['lon'] = df_poll['station'].apply(lambda x: station_coords[x][1])
        
        # Marker
        marker_fg = folium.FeatureGroup(name=f"{pollutant} - Marker", show=False)
        for idx, row in df_poll.iterrows():
            radius = 5 + row[pollutant] * scaling[pollutant]
            popup_text = f"<b>Stasiun:</b> {row['station']}<br><b>{pollutant}:</b> {row[pollutant]:.1f}"
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                popup=popup_text,
                color=colors[pollutant],
                fill=True,
                fill_color=colors[pollutant],
                fill_opacity=0.7
            ).add_to(marker_fg)
        marker_fg.add_to(base_map)
        
        # Heatmap
        heat_fg = folium.FeatureGroup(name=f"{pollutant} - Heatmap", show=True)
        heat_data = df_poll[['lat', 'lon', pollutant]].values.tolist()
        HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=25,
            blur=15,
            max_zoom=10
        ).add_to(heat_fg)
        heat_fg.add_to(base_map)
    
    folium.LayerControl(collapsed=False).add_to(base_map)
    return base_map


###############################
# 2. BAGIAN UTAMA STREAMLIT APP
###############################

def main():
    st.set_page_config(
        page_title="Air Pollution Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("Air Pollution Interactive Dashboard")
    
    # Bagian Sidebar
    st.sidebar.title("Pengaturan Dashboard")
    
    # Input path data folder (sesuaikan dengan struktur di Streamlit Cloud)
    data_folder = st.sidebar.text_input(
        "Folder Data CSV",
        value="data",
        help="Masukkan path folder tempat file-file CSV disimpan."
    )
    
    # Tombol untuk load data
    if st.sidebar.button("Load Data"):
        with st.spinner("Loading..."):
            df = load_data(data_folder=data_folder)
        st.session_state["df"] = df
    
    # Pastikan data sudah ada di session_state
    if "df" not in st.session_state:
        st.warning("Silakan klik 'Load Data' terlebih dahulu.")
        return
    
    df = st.session_state["df"]
    
    # Menampilkan sekilas data
    st.subheader("Preview Data")
    st.write(df.head(10))
    st.write("Shape:", df.shape)
    
    # Pilihan tab: Overview, EDA, Tren, Peta
    tabs = st.tabs(["Overview", "Exploratory Data Analysis", "Tren Per Tahun & Stasiun", "Visualisasi Peta"])
    
    #########################
    # TAB 1: OVERVIEW
    #########################
    with tabs[0]:
        st.subheader("Overview Statistik")
        
        numeric_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
        # Descriptive stats
        desc = df[numeric_cols].describe()
        st.write(desc)
        
        # Menampilkan Missing Value
        st.write("Jumlah Missing Value per Kolom:")
        st.write(df.isna().sum())
        
    #########################
    # TAB 2: EDA
    #########################
    with tabs[1]:
        st.subheader("Exploratory Data Analysis")
        
        # Pilihan untuk menampilkan histogram/boxplot
        plot_type = st.radio("Tipe Plot:", ["Histogram", "Boxplot"], horizontal=True)
        col_selected = st.selectbox("Pilih Kolom Numerik:", numeric_cols)
        
        if plot_type == "Histogram":
            fig, ax = plt.subplots(figsize=(7,4))
            ax.hist(df[col_selected].dropna(), bins=30)
            ax.set_title(f"Histogram {col_selected}")
            st.pyplot(fig)
            
        else:  # Boxplot
            fig, ax = plt.subplots(figsize=(4,4))
            sns.boxplot(y=df[col_selected], ax=ax)
            ax.set_title(f"Boxplot {col_selected}")
            st.pyplot(fig)
        
        # Korelasi Heatmap
        if st.checkbox("Tampilkan Korelasi Heatmap (antara seluruh numeric_cols)"):
            corr_matrix = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(8,6))
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)
    
    #########################
    # TAB 3: Tren Per Tahun & Stasiun
    #########################
    with tabs[2]:
        st.subheader("Analisis Tren Per Tahun & Stasiun")
        
        if 'timestamp' in df.columns:
            # Buat kolom year
            df['year'] = df['timestamp'].dt.year
            
            pollutants = ['PM2.5','PM10','SO2','NO2','CO','O3']
            
            # Agregasi per tahun
            annual_avg = df.groupby('year')[pollutants].mean().reset_index()
            
            st.markdown("**Rata-rata tahunan tiap polutan (seluruh stasiun):**")
            st.dataframe(annual_avg)
            
            # Visualisasi tren tahunan
            st.markdown("**Line Chart Tren Polutan per Tahun:**")
            fig, ax = plt.subplots(figsize=(10,5))
            for pollutant in pollutants:
                ax.plot(annual_avg['year'], annual_avg[pollutant], marker='o', label=pollutant)
            ax.set_xlabel("Tahun")
            ax.set_ylabel("Rata-rata Konsentrasi")
            ax.set_title("Tren Tahunan Polutan Udara")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
            
            # Analisis tren per stasiun: slope
            st.markdown("---")
            st.markdown("**Slope Tren Tahunan per Stasiun (linregress)**")
            stations = df['station'].unique()
            
            station_trends = {}
            for station in stations:
                station_data = df[df['station'] == station].copy()
                annual_station = station_data.groupby('year')[pollutants].mean().reset_index()
                slopes = {}
                for pollutant in pollutants:
                    if len(annual_station) >= 2:
                        slope, intercept, r_value, p_value, std_err = linregress(
                            annual_station['year'], annual_station[pollutant]
                        )
                        slopes[pollutant] = slope
                    else:
                        slopes[pollutant] = np.nan
                station_trends[station] = slopes
            
            station_trends_df = pd.DataFrame(station_trends).T
            station_trends_df.columns = [f"slope_{c}" for c in station_trends_df.columns]
            st.dataframe(station_trends_df)
            
        else:
            st.error("Tidak ditemukan kolom 'timestamp' untuk analisis tren.")
    
    #########################
    # TAB 4: VISUALISASI PETA
    #########################
    with tabs[3]:
        st.subheader("Peta Interaktif Folium")
        
        pollutants_for_map = st.multiselect(
            "Pilih Polutan yang akan ditampilkan pada Peta:",
            ['PM2.5','PM10','SO2','NO2','CO','O3'],
            default=['PM2.5','PM10']
        )
        
        # Pastikan kolom lat/lon untuk stasiun
        # (Di sini kita asumsikan stasiun Koordinat Hardcode di create_folium_map)
        
        # Buat peta Folium
        folium_map = create_folium_map(df, pollutants_for_map)
        
        # Tampilkan peta di Streamlit
        st_data = st_folium(folium_map, width=900, height=600)

    st.markdown("---")
    st.info("Dashboard ini dibuat dengan Streamlit. \n\nSilakan eksplor setiap tab di atas untuk melihat data, analisis, dan visualisasi interaktif.")


if __name__ == "__main__":
    main()
