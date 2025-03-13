# dashboard.py

import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')
@st.cache_data
def load_data(folder_path: str):
    """
    Menggabungkan semua file CSV di folder_path menjadi satu DataFrame.
    Jika kolom 'year','month','day','hour' tersedia, buat kolom 'timestamp'.
    """
    all_files = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            df_temp = pd.read_csv(file_path)
            all_files.append(df_temp)
    
    if not all_files:
        st.error("Tidak ditemukan file CSV di folder tersebut.")
        return pd.DataFrame()
    
    df = pd.concat(all_files, ignore_index=True)

    # Jika ada kolom year, month, day, hour, kita buat timestamp
    needed_cols = ['year','month','day','hour']
    if all(col in df.columns for col in needed_cols):
        df['timestamp'] = pd.to_datetime(df[needed_cols])
    
    return df


def main():
    st.set_page_config(
        page_title="Air Quality Interactive Dashboard",
        layout="wide"
    )
    
    st.title("Air Quality Interactive Dashboard")
    st.write("""
        **Selamat datang!** Dashboard ini menampilkan **beberapa visualisasi interaktif** 
        dalam satu halaman. Silakan gunakan **sidebar** untuk melakukan berbagai **filter** 
        (tanggal, stasiun, rentang PM2.5, rentang PM10) serta memilih **kolom** untuk 
        visualisasi _Histogram_, _Time Series_, _Scatter Plot_, dan _Bar Chart_.
    """)
    
    folder_path = st.sidebar.text_input(
        "Masukkan Folder Path CSV:",
        value="submission/dashboard/data",
        help="Silakan ganti path sesuai lokasi CSV Anda"
    )
    
    if st.sidebar.button("Load Data"):
        with st.spinner("Loading data..."):
            df = load_data(folder_path)
        st.session_state["df"] = df
    
    if "df" not in st.session_state:
        st.warning("Silakan klik 'Load Data' untuk memuat dataset.")
        return
    
    df = st.session_state["df"].copy()
    if df.empty:
        st.error("DataFrame kosong atau format CSV tidak sesuai.")
        return
    
    if "timestamp" in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        date_range = st.sidebar.date_input(
            "Filter Rentang Tanggal",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
    
    if "station" in df.columns:
        all_stations = sorted(df['station'].dropna().unique())
        chosen_stations = st.sidebar.multiselect(
            "Pilih Stasiun:",
            all_stations,
            default=all_stations 
        )
        df = df[df['station'].isin(chosen_stations)]
    
    if "PM2.5" in df.columns:
        min_pm25_val = float(df["PM2.5"].min())
        max_pm25_val = float(df["PM2.5"].max())
        pm25_slider = st.sidebar.slider(
            "Rentang PM2.5",
            min_value=min_pm25_val,
            max_value=max_pm25_val,
            value=(min_pm25_val, max_pm25_val)
        )
        df = df[(df["PM2.5"] >= pm25_slider[0]) & (df["PM2.5"] <= pm25_slider[1])]
    
    if "PM10" in df.columns:
        min_pm10_val = float(df["PM10"].min())
        max_pm10_val = float(df["PM10"].max())
        pm10_slider = st.sidebar.slider(
            "Rentang PM10",
            min_value=min_pm10_val,
            max_value=max_pm10_val,
            value=(min_pm10_val, max_pm10_val)
        )
        df = df[(df["PM10"] >= pm10_slider[0]) & (df["PM10"] <= pm10_slider[1])]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.error("Tidak ada kolom numerik untuk divisualisasikan.")
        return
    st.markdown("---")
    st.header("Dashboard Interaktif")
    st.write("Silakan pilih kolom yang Anda inginkan di setiap chart.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1) Histogram")
        hist_col = st.selectbox("Pilih kolom numeric (Histogram):", numeric_cols, key="hist_col")
        if hist_col and not df[hist_col].dropna().empty:
            fig, ax = plt.subplots(figsize=(5,4))
            sns.histplot(df[hist_col], bins=30, kde=True, ax=ax)
            ax.set_title(f"Histogram {hist_col}")
            ax.set_xlabel(hist_col)
            ax.set_ylabel("Frekuensi")
            st.pyplot(fig)
        else:
            st.warning(f"Tidak ada data atau kolom {hist_col} kosong setelah filter.")
        
        st.caption(f"""
            *Insight:* Dengan histogram di atas, Anda bisa melihat sebaran nilai **{hist_col}** 
            setelah menerapkan semua filter di sidebar.
        """)
    
    with col2:
        st.subheader("2) Time Series (Line Chart)")
        if "timestamp" in df.columns and not df["timestamp"].dropna().empty:
            time_col = st.selectbox("Pilih kolom numeric (Time Series):", numeric_cols, key="time_col")
            if time_col:
                df_sorted = df.dropna(subset=["timestamp", time_col]).sort_values("timestamp")
                if not df_sorted.empty:
                    fig, ax = plt.subplots(figsize=(5,4))
                    ax.plot(df_sorted["timestamp"], df_sorted[time_col], marker='o', linestyle='-')
                    ax.set_title(f"Time Series: {time_col} vs. Timestamp")
                    ax.set_xlabel("Timestamp")
                    ax.set_ylabel(time_col)
                    plt.xticks(rotation=30)
                    st.pyplot(fig)
                else:
                    st.warning("Data Time Series kosong setelah filter.")
        else:
            st.warning("Kolom 'timestamp' tidak tersedia/valid, tidak bisa menampilkan Time Series.")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("3) Scatter Plot (X vs Y)")
        
        scatter_x = st.selectbox("Pilih X-axis (numeric):", numeric_cols, key="scatter_x")
        scatter_y = st.selectbox("Pilih Y-axis (numeric):", numeric_cols, key="scatter_y")
        
        if scatter_x and scatter_y:
            df_scatter = df.dropna(subset=[scatter_x, scatter_y])
            if not df_scatter.empty:
                fig, ax = plt.subplots(figsize=(5,4))
                sns.scatterplot(data=df_scatter, x=scatter_x, y=scatter_y, ax=ax)
                ax.set_title(f"Scatter Plot: {scatter_x} vs {scatter_y}")
                st.pyplot(fig)
            else:
                st.warning("Data Scatter kosong setelah filter.")
        else:
            st.warning("Pilih kolom numeric X dan Y untuk scatter plot.")
    
    with col4:
        st.subheader("4) Bar Chart: Rata-rata per Stasiun")
        if "station" in df.columns and not df["station"].dropna().empty:
            bar_col = st.selectbox("Pilih kolom numeric (Bar Chart):", numeric_cols, key="bar_col")
            if bar_col:
                # Group by station
                df_bar = df.dropna(subset=["station", bar_col])
                if not df_bar.empty:
                    # Pilih aggregator
                    agg_choice = st.radio("Pilih aggregator:", ["mean", "median"], horizontal=True, key="agg_choice")
                    if agg_choice == "mean":
                        station_stat = df_bar.groupby("station")[bar_col].mean().sort_values(ascending=False)
                    else:
                        station_stat = df_bar.groupby("station")[bar_col].median().sort_values(ascending=False)
                    
                    # Buat Bar Chart
                    fig, ax = plt.subplots(figsize=(6,4))
                    station_stat.plot(kind="bar", ax=ax)
                    ax.set_title(f"{agg_choice.title()} {bar_col} per Stasiun")
                    ax.set_xlabel("Stasiun")
                    ax.set_ylabel(f"{bar_col} ({agg_choice})")
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.warning("Data Bar Chart kosong setelah filter.")
        else:
            st.warning("Kolom 'station' tidak ada, tidak bisa membuat bar chart per stasiun.")
    
    st.markdown("---")
    st.info("""
    **Catatan**:
    - Anda dapat memodifikasi filter maupun pilihan kolom di _sidebar_ agar sesuai kebutuhan.
    - Setiap _chart_ di atas akan otomatis berubah berdasarkan hasil filter.
    - Tidak ada tabel yang ditampilkan; hanya visual interaktif.
    """)


if __name__ == "__main__":
    main()
