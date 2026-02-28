import pandas as pd

# Dosyaları oku
df_concepts = pd.read_csv("openalex_with_concepts.csv", usecols=["title", "concepts"])
df_openalex = pd.read_csv("openalex.csv")

# Tekrarlanan title'ları concepts dosyasında kaldır
df_concepts = df_concepts.drop_duplicates(subset=["title"])

# Merge işlemi title üzerinden
df_merged = pd.merge(df_openalex, df_concepts, on="title", how="left")

# abstract sütununun yanına concepts sütunu gelecek şekilde sütun sırasını değiştir
columns = list(df_merged.columns)
abstract_index = columns.index("abstract")
columns.remove("concepts")
columns.insert(abstract_index + 1, "concepts")
df_merged = df_merged[columns]

# Tüm dataframe'deki duplicate satırları tamamen kaldır (opsiyonel, title ve diğer sütun bazlı)
df_merged = df_merged.drop_duplicates()

# Sonucu yeni CSV olarak kaydet
df_merged.to_csv("openalex_with_concepts_filled.csv", index=False)

print("Concepts sütunu abstract'ın yanına eklendi ve duplicate satırlar kaldırıldı. Dosya 'openalex_with_concepts_filled.csv' olarak kaydedildi.")