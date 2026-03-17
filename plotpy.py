import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import statsmodels.api as sm

# Excel dosyasını oku
df = pd.read_excel("yearly_theory_distribution.xlsx")

years = df['publication_year'].to_numpy()
years_scaled = years - years.min()  # numerik stabilite

selected_theories = [
    "Contingency Theory",
    "Resource Dependence Theory",
    "Resource-Based View (RBV)",
    "Transaction Cost Theory"
]

# ---------- MODELLER ----------

def exponential_model(x, a, b):
    return a * np.exp(b * x)

def logarithmic_model(x, a, b):
    return a + b * np.log(x + 1)

def polynomial_model(x, a, b, c):
    return a*x**2 + b*x + c

def linear_model(x, a, b):
    return a*x + b

# ---------- OLS F-TEST FONKSİYONU ----------

def calculate_fisher_test(X, y):
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    return model.fvalue, model.f_pvalue

# ---------- MODEL ÇALIŞTIRICI ----------

def run_model(model_name):

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"{model_name} Trend", fontsize=16)

    for i, theory in enumerate(selected_theories):

        counts = df[theory].to_numpy()

        if model_name == "Exponential":
            params, _ = curve_fit(exponential_model, years_scaled, counts, maxfev=20000)
            fit_line = exponential_model(years_scaled, *params)
            X = years_scaled.reshape(-1, 1)

        elif model_name == "Logarithmic":
            params, _ = curve_fit(logarithmic_model, years_scaled, counts, maxfev=20000)
            fit_line = logarithmic_model(years_scaled, *params)
            X = np.log(years_scaled + 1).reshape(-1, 1)

        elif model_name == "Polynomial":
            params, _ = curve_fit(polynomial_model, years_scaled, counts, maxfev=20000)
            fit_line = polynomial_model(years_scaled, *params)
            X = np.column_stack((years_scaled, years_scaled**2))

        elif model_name == "Linear":
            params, _ = curve_fit(linear_model, years_scaled, counts)
            fit_line = linear_model(years_scaled, *params)
            X = years_scaled.reshape(-1, 1)

        # R2
        r2 = r2_score(counts, fit_line)

        # Fisher (F-test)
        F_stat, p_value = calculate_fisher_test(X, counts)

        row = i // 2
        col = i % 2
        ax = axs[row, col]

        ax.plot(years, counts, 'o-', color='blue', label="Data")
        ax.plot(years, fit_line, '-', color='red',
                label=f"{model_name} Fit\n$R^2$={r2:.3f}\nF={F_stat:.2f}\np={p_value:.4f}")

        ax.set_title(theory)
        ax.set_xlabel("Year")
        ax.set_ylabel("Publications")
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    plt.show()


# ---------- SIRAYLA ÇALIŞTIR ----------

run_model("Exponential")
run_model("Logarithmic")
run_model("Polynomial")
run_model("Linear")