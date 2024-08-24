import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from babel.numbers import format_currency

# Mengatur style Seaborn
sns.set(style='dark')

# Mengatur opsi Streamlit
st.set_option('deprecation.showPyplotGlobalUse', False)

# Membaca dataset
all_df = pd.read_csv("bike_merge.csv")

# Mengubah kolom menjadi format datetime
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Menampilkan pengantar analisis di Streamlit
st.write(
    """
    # Hasil Analisis Dataset Bike Sharing :bike:
    Analisis ini akan menguraikan beberapa pertanyaan penting yang mungkin relevan bagi pemilik bisnis, di antaranya:
    1. Musim apa yang memiliki jumlah penyewaan sepeda tertinggi?
    2. Seberapa sering pelanggan menyewa sepeda dalam beberapa bulan terakhir?
    3. Bagaimana pola penyewaan sepeda berdasarkan jam? Pada jam berapa terjadi peningkatan penyewaan?
    """
)

# Mendapatkan rentang tanggal dari data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

# Sidebar untuk pemilihan rentang tanggal
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu Data: ',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Fungsi untuk membuat DataFrame pesanan harian
def create_daily_orders_df(df):
    daily_orders_df = df.resample('D', on='dteday').agg({
        "cnt_daily": "sum"
    }).reset_index().rename(columns={"cnt_daily": "order_count"})
    
    return daily_orders_df

# Fungsi untuk membuat DataFrame berdasarkan musim
def create_byseason_df(df):
    byseason_df = df.groupby("season_daily").cnt_daily.nunique().reset_index()
    byseason_df.rename(columns={"cnt_daily": "customer_count", "season_daily": "season"}, inplace=True)
    
    return byseason_df

# Fungsi untuk membuat DataFrame Recency dan Frequency
def create_rf_df(df):
    tanggal_sekarang = df['dteday'].max()
    rf_df = df.groupby("mnth_daily", as_index=False).agg({
        'dteday': lambda x: (tanggal_sekarang - x.max()).days,
        'cnt_daily': 'count'
    }).rename(columns={
        'mnth_daily': 'month',
        'dteday': 'recency',
        'cnt_daily': 'frequency'
    })
    
    return rf_df

# Filter data berdasarkan tanggal yang dipilih
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]
byseason_df = create_byseason_df(main_df)
daily_orders_df = create_daily_orders_df(main_df)

# Visualisasi data berdasarkan musim
st.title("Demografi Pelanggan")
st.subheader("Jumlah Pelanggan Berdasarkan Musim :fallen_leaf:")

fig, ax = plt.subplots(figsize=(20, 10))
colors1 = ["#D3D3D3", "#D3D3D3", "#FFC0CB", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="season", 
    y="customer_count", 
    data=byseason_df.sort_values(by="customer_count", ascending=False),
    palette=colors1, 
    ax=ax
)

ax.set_title("Jumlah Pelanggan Berdasarkan Musim", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=25)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# Menampilkan informasi musim
st.markdown("## Masing-masing angka pada plot mewakili musim:")
st.markdown("1 -> Cerah, Sedikit berawan, Sebagian berawan")
st.markdown("2 -> Berkabut + Berawan, Berkabut + Awan terpecah, Berkabut + Sedikit berawan")
st.markdown("3 -> Salju ringan, Hujan ringan + Petir + Awan tersebar")
st.markdown("4 -> Hujan deras + Es batu + Petir + Kabut, Salju + Kabut")

# Fungsi untuk interpretasi pertanyaan pertama
def main1():
    st.title("Interpretasi untuk Pertanyaan Ke-1")

    if st.button("Tampilkan Keterangan 1"):
        st.success("Jumlah pelanggan terbanyak tercatat saat musim salju ringan dan hujan ringan dengan petir serta awan tersebar. Ini menunjukkan bahwa pelanggan cenderung menyewa sepeda ketika cuaca tidak terlalu panas, membuatnya nyaman untuk bersepeda.")

if __name__ == "__main__":
    main1()

# Membuat DataFrame Recency dan Frequency
rf_df = create_rf_df(all_df)

# Menampilkan DataFrame RF
st.title("Analisis RF :mag:")
st.subheader("Recency dan Frequency pada Setiap Bulan:")
st.write(rf_df)

# Menampilkan metrik rata-rata Recency dan Frequency
avg_recency = round(rf_df.recency.mean(), 1)
avg_frequency = round(rf_df.frequency.mean(), 2)

col1, col2 = st.columns(2)
with col1:
    st.metric("Rata-rata Recency (hari)", value=avg_recency)

with col2:
    st.metric("Rata-rata Frequency", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 15))

# Plot untuk Recency
recency_df = rf_df.sort_values(by="recency", ascending=True).head(12)
colors_recency = ["#90CAF9"] * len(recency_df)
sns.barplot(y="recency", x="month", data=recency_df, palette=colors_recency, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Bulan ke-", fontsize=30)
ax[0].set_title("Berdasarkan Recency", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# Plot untuk Frequency
frequency_df = rf_df.sort_values(by="frequency", ascending=False).head(12)
colors_frequency = ["#90CAF9"] * len(frequency_df)
sns.barplot(y="frequency", x="month", data=frequency_df, palette=colors_frequency, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Bulan ke-", fontsize=30)
ax[1].set_title("Berdasarkan Frequency", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

# Fungsi untuk interpretasi pertanyaan kedua
def main2():
    st.title("Interpretasi untuk Pertanyaan Ke-2")

    if st.button("Tampilkan Keterangan 2"):
        st.success("Dalam beberapa bulan terakhir, banyak pelanggan yang sering menyewa sepeda, yang terlihat dari nilai recency yang rendah dan frekuensi yang tinggi.")

if __name__ == "__main__":
    main2()

# Menyiapkan data untuk analisis pola waktu penyewaan
all_df.set_index('dteday', inplace=True)

# Judul
st.title("Pola Waktu Penyewaan Sepeda")

# Pilih rentang jam menggunakan slider
selected_hour_range = st.slider("Pilih Rentang Jam", min_value=0, max_value=23, value=(0, 23))

# Memfilter data berdasarkan rentang jam yang dipilih
selected_data = all_df[(all_df['hr'] >= selected_hour_range[0]) & (all_df['hr'] <= selected_hour_range[1])]

# Plot pola waktu penyewaan sepeda
plt.figure(figsize=(12, 6))
sns.lineplot(x='hr', y='cnt_hourly', data=selected_data, ci=None, color='blue')
plt.title("Pola Penyewaan Sepeda Harian Berdasarkan Waktu")
plt.xlabel("Jam")
plt.ylabel("Jumlah Penyewa Sepeda Harian")
plt.xticks(rotation=45, ha='right')

st.pyplot(plt.gcf())

# Fungsi untuk interpretasi pertanyaan ketiga
def main3():
    st.title("Interpretasi Grafik untuk Pertanyaan Ke-3")

    if st.button("Tampilkan Keterangan 3"):
        st.success("Penyewaan sepeda cenderung meningkat pada sore hari, terutama antara jam 16.00 hingga 17.00, menunjukkan waktu yang populer bagi pelanggan untuk bersepeda.")

if __name__ == "__main__":
    main3()
