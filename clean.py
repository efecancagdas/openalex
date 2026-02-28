import pandas as pd

# CSV dosyasını oku
df = pd.read_csv('openalex_limited.csv')

# 'abstract' sütununda NaN (boş) olan satırları sil
df_cleaned = df.dropna(subset=['abstract'])

# Temizlenmiş veriyi yeni bir dosyaya kaydet
df_cleaned.to_csv('openalex_cleaned.csv', index=False)

# Bilgi yazdır
print(f"Orijinal satır sayısı: {len(df)}")
print(f"Temizlendikten sonraki satır sayısı: {len(df_cleaned)}")
print(f"Silinen satır sayısı: {len(df) - len(df_cleaned)}")