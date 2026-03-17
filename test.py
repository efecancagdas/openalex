import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit

# -------------------------
# STATIC DATA
# -------------------------

years = np.array([2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025])
quantity = np.array([7,12,27,46,41,63,64,58,74,86,66,86,108])

# Scale years for numerical stability
years_scaled = years - years.min()

# -------------------------
# MODELS
# -------------------------

def exponential_model(x, a, b):
    return a * np.exp(b * x)

def logarithmic_model(x, a, b):
    return a + b * np.log(x + 1)

def polynomial_model(x, a, b, c):
    return a*x**2 + b*x + c

def linear_model(x, a, b):
    return a*x + b

# -------------------------
# FUNCTION TO RUN & PLOT
# -------------------------

def run_model(model_name):

    if model_name == "Exponential":
        params, _ = curve_fit(exponential_model, years_scaled, quantity, maxfev=20000)
        fit = exponential_model(years_scaled, *params)

    elif model_name == "Logarithmic":
        params, _ = curve_fit(logarithmic_model, years_scaled, quantity, maxfev=20000)
        fit = logarithmic_model(years_scaled, *params)

    elif model_name == "Polynomial (Degree 2)":
        params, _ = curve_fit(polynomial_model, years_scaled, quantity)
        fit = polynomial_model(years_scaled, *params)

    elif model_name == "Linear":
        params, _ = curve_fit(linear_model, years_scaled, quantity)
        fit = linear_model(years_scaled, *params)

    r2 = r2_score(quantity, fit)

    plt.figure(figsize=(8,5))

    # 🔵 Blue connected data with markers
    plt.plot(years, quantity, 'o-', color='blue', label="Data")

    # 🔴 Red trendline
    plt.plot(years, fit, '-', color='red',
             label=f"{model_name} Fit\nR² = {r2:.3f}")

    plt.xlabel("Year")
    plt.ylabel("Quantity")
    plt.title(f"{model_name} Trend")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# -------------------------
# RUN SEQUENTIALLY
# -------------------------

run_model("Exponential")
run_model("Logarithmic")
run_model("Polynomial (Degree 2)")
run_model("Linear")