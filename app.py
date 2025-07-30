import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
import random

st.set_page_config(page_title="Dashboard Review Restoran", layout="wide")
st.markdown("<h1 style='text-align: center; color: #6c5ce7;'>🍽️ Dashboard Analisis Review Restoran</h1>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("review_restoran_scraped_2025.csv")
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    df = df.dropna(subset=['Komentar', 'Rating'])
    return df

df = load_data()

# Fungsi sentiment yang lebih realistis
def better_sentiment(text, rating):
    blob = TextBlob(str(text))
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    elif rating <= 2:
        return 'Negative'
    elif rating == 3:
        return 'Neutral'
    else:
        return 'Positive'

# Analisis sentimen dengan kombinasi TextBlob + rating
df['Sentiment'] = df.apply(lambda x: better_sentiment(x['Komentar'], x['Rating']), axis=1)

# Sidebar filter
st.sidebar.header("🎯 Filter Data")
rating_filter = st.sidebar.slider("Rating", 1, 5, (1, 5))
restaurant_options = df['Nama Restoran'].dropna().unique().tolist()
selected_restaurant = st.sidebar.selectbox("Pilih Restoran", ["Semua"] + restaurant_options)
start_date = st.sidebar.date_input("Tanggal Mulai", df['Tanggal'].min().date())
end_date = st.sidebar.date_input("Tanggal Akhir", df['Tanggal'].max().date())

# Filter data
filtered_df = df[
    (df['Rating'] >= rating_filter[0]) &
    (df['Rating'] <= rating_filter[1]) &
    (df['Tanggal'] >= pd.to_datetime(start_date)) &
    (df['Tanggal'] <= pd.to_datetime(end_date))
]
if selected_restaurant != "Semua":
    filtered_df = filtered_df[filtered_df['Nama Restoran'] == selected_restaurant]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Statistik", 
    "📈 Distribusi Rating", 
    "☁️ WordCloud", 
    "📉 Rating vs Panjang Komentar", 
    "📄 Data Mentah"
])

# Tab 1 - Statistik
with tab1:
    st.markdown("### 🔢 Statistik Review")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Review", len(filtered_df))
    col2.metric("Rata-rata Rating", f"{filtered_df['Rating'].mean():.2f}")
    col3.metric("Review Positif", f"{(filtered_df['Sentiment'] == 'Positive').mean()*100:.1f}%")
    col4.metric("Review Negatif", f"{(filtered_df['Sentiment'] == 'Negative').mean()*100:.1f}%")

# Tab 2 - Distribusi Rating
with tab2:
    st.markdown("### 📈 Distribusi Rating")
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    sns.countplot(data=filtered_df, x='Rating', palette='Set2', ax=ax1)
    ax1.set_title("Distribusi Rating", fontsize=14)
    st.pyplot(fig1)

# Tab 3 - WordCloud
with tab3:
    st.markdown("### ☁️ WordCloud Komentar")
    text = " ".join(filtered_df['Komentar'].dropna().astype(str).tolist())
    wordcloud = WordCloud(width=1000, height=300, background_color='white', colormap='Set2').generate(text)
    fig2, ax2 = plt.subplots(figsize=(10, 3.5))
    ax2.imshow(wordcloud, interpolation='bilinear')
    ax2.axis('off')
    st.pyplot(fig2)

# Tab 4 - Scatter Plot Rating vs Panjang Komentar
with tab4:
    st.markdown("### 📉 Rating vs Panjang Komentar")
    filtered_df['Panjang Komentar'] = filtered_df['Komentar'].apply(len)
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=filtered_df, x="Rating", y="Panjang Komentar", ax=ax3)
    st.pyplot(fig3)

# Tab 5 - Tabel Data
with tab5:
    st.markdown("### 📄 Data Mentah")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Data CSV", data=csv, file_name='filtered_reviews.csv', mime='text/csv')
