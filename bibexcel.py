import pandas as pd
import os

# CSV dosyasını oku
df = pd.read_csv('openalex_cleaned_theory.csv')

# Output klasörü oluştur
output_folder = 'theory_docs'
os.makedirs(output_folder, exist_ok=True)

# Tek bir merged dosya için liste
merged_lines = []

# Core_Theory_Group bazında gruplandır
for theory_group, group_df in df.groupby('Core_Theory_Group'):
    # Dosya adı olarak teoriyi kullan, boşlukları alt çizgi yap
    file_name = f"{theory_group.replace(' ', '_')}.doc"
    file_path = os.path.join(output_folder, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        for _, row in group_df.iterrows():
            # Her şey büyük harf, başta/sonda tırnak yok
            lines = [
                'PT- J|',
                f'TI- {str(row["title"]).upper()}|',
                f'AB- {str(row["abstract"]).upper()}|',
                f'DE- {str(row["concepts"]).upper()}|',
                ''
            ]
            f.write('\n'.join(lines) + '\n')

            # merged dosya için de ekle
            merged_lines.extend(lines + [''])

# Merged dosyayı oluştur
merged_path = os.path.join(output_folder, 'merged.doc')
with open(merged_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(merged_lines))