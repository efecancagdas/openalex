import pandas as pd

# CSV dosyasını oku
input_file = "openalex_cleaned_theory.csv"
df = pd.read_csv(input_file, encoding="utf-8-sig")

# Core_Theory_Group sütununda frekans analizi
frequency = df['Core_Theory_Group'].value_counts().reset_index()
frequency.columns = ['Core_Theory_Group', 'Count']

# Excel olarak kaydet (encoding kaldırıldı)
output_file = "theory_frequency.xlsx"
frequency.to_excel(output_file, index=False)

print(f"✅ Frekans tablosu oluşturuldu ve kaydedildi: {output_file}")
print(frequency)