import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Excel dosyasını oku
df = pd.read_excel("yearly_theory_distribution.xlsx")

# Seçilecek 4 temel teori
selected_theories = [
    "Contingency Theory",
    "Resource Dependence Theory",
    "Resource-Based View (RBV)",
    "Transaction Cost Theory"
]

# Tüm teori sütunlarını al (publication_year hariç)
theory_columns = df.columns.tolist()
theory_columns.remove('publication_year')

cagr_values_all = []
cagr_values_selected = []

print("CAGR Values by Theory (Starting from first publication year):")
for theory in theory_columns:
    series = df[theory]

    # İlk pozitif değeri bul
    pos_idx = series.ne(0).idxmax()
    start_value = series.iloc[pos_idx]
    start_year = df['publication_year'].iloc[pos_idx]

    # Son yıl verisi
    end_value = series.iloc[-1]
    end_year = df['publication_year'].iloc[-1]

    # Yıl sayısı (başlangıç ve bitiş dahil)
    n_years = end_year - start_year + 1

    # CAGR hesapla
    if start_value == 0:
        cagr = 0
    else:
        cagr = (end_value / start_value) ** (1 / (n_years - 1)) - 1

    cagr_percent = cagr * 100
    cagr_values_all.append((theory, cagr_percent))

    # Print ile göster
    print(f"{theory}: {cagr_percent:.2f}% (from {start_year} to {end_year})")

    # Eğer seçimdeyse grafiğe ekle
    if theory in selected_theories:
        cagr_values_selected.append(cagr_percent)

# Grafikte sadece seçilmiş 4 teoriyi göster
plt.figure(figsize=(10, 6))
plt.bar(selected_theories, cagr_values_selected, color='skyblue')
plt.ylabel('CAGR (%)')
plt.title('Compound Annual Growth Rate (CAGR)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()