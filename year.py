import pandas as pd

# CSV dosyasını oku
df = pd.read_csv("openalex_cleaned_theory.csv")

# Sadece gerekli sütunları al
df = df[['Core_Theory_Group', 'publication_year']]

# Yıllara göre teorilerin yayın sayısını hesapla
pivot_table = df.pivot_table(index='Core_Theory_Group',
                             columns='publication_year',
                             aggfunc='size',
                             fill_value=0)

# Pivot table'ı transpoze et: yıllar satır, teoriler sütun
pivot_table = pivot_table.T  # T harfi transpose

# Excel dosyası oluştur ve kaydet
with pd.ExcelWriter("yearly_theory_distribution.xlsx", engine='openpyxl') as writer:
    # Yıllara göre yayın sayısı tablosu (transpoze edilmiş)
    pivot_table.to_excel(writer, sheet_name='Yearly_Publications')

    # CAGR hesaplama
    cagr_list = []
    for theory in pivot_table.columns:  # teoriler sütun
        years = pivot_table.index
        # İlk 0 olmayan yıl
        start_year = None
        for y in years:
            if pivot_table.loc[y, theory] > 0 and y <= 2025:
                start_year = y
                break
        if start_year is None:
            continue

        end_year = 2025
        start_value = pivot_table.loc[start_year, theory]
        end_value = pivot_table.loc[end_year, theory] if end_year in pivot_table.index else 0
        n_years = end_year - start_year

        if start_value == 0 or n_years == 0:
            cagr = None
        else:
            cagr = (end_value / start_value) ** (1 / n_years) - 1

        cagr_list.append({
            'Core_Theory_Group': theory,
            'Start_Year': start_year,
            'End_Year': end_year,
            'Start_Value': start_value,
            'End_Value': end_value,
            'CAGR': cagr
        })

    cagr_df = pd.DataFrame(cagr_list)
    cagr_df.to_excel(writer, sheet_name='CAGR', index=False)

print("Excel dosyası 'yearly_theory_distribution.xlsx' olarak kaydedildi.")