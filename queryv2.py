import pandas as pd
import subprocess
import time
import os
import glob
import re
import tkinter as tk
from tkinter import ttk, messagebox

# =========================
# AYARLAR
# =========================

INPUT_FILE = "openalex_cleaned.csv"
THEORY_FILE = "Core_Management_Theories.xlsx"
OUTPUT_FILE = "openalex_cleaned_theory.csv"

OLLAMA_PATH = r"C:\Users\EFE\AppData\Local\Programs\Ollama\ollama.exe"

# 🌟 Desteklenen modeller ve parsing ayarları
MODEL_OPTIONS = {
    "gemma3:12b": {"parsing": "start", "phrase": None},
    "llama3.1:8b": {"parsing": "start", "phrase": None},
    "deepseek-r1:8b": {"parsing": "after", "phrase": "...done thinking."},
}

PART_SIZE = 200
TIMEOUT_SECONDS = 60
MAX_RETRY = 2

# =========================
# TKINTER MODEL SEÇİM PENCERESİ
# =========================

selected_model = None

def choose_model():
    global selected_model
    selected_model = combo.get()
    if not selected_model:
        messagebox.showerror("Hata", "Bir model seçmelisiniz!")
        root.destroy()
        exit()
    root.destroy()

root = tk.Tk()
root.title("Model Seçimi")
root.geometry("300x120")
root.resizable(False, False)

tk.Label(root, text="Çalıştırılacak modeli seçin:").pack(pady=10)
combo = ttk.Combobox(root, values=list(MODEL_OPTIONS.keys()), state="readonly")
combo.pack(pady=5)
combo.current(0)
tk.Button(root, text="Seç", command=choose_model).pack(pady=10)

root.mainloop()

MODEL_NAME = selected_model
MODEL_PARSING = MODEL_OPTIONS[MODEL_NAME]

# =========================
# TOPLAM SATIR SAYISI
# =========================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    total_rows = sum(1 for _ in f) - 1  # header hariç

print(f"🔎 LLM ile sınıflandırma başlıyor ({total_rows} makale)...")

# =========================
# EXCEL'DEN TEORİ PROMPT'U OLUŞTURMA
# =========================

df_theories = pd.read_excel(THEORY_FILE)

numbered_theory_list = []
for idx, row in df_theories.iterrows():
    theory_name = row["Theory"]
    explanation = str(row.get("Explanation", ""))
    keywords = str(row.get("Keywords", ""))
    core_assumption = str(row.get("Core Assumption", ""))
    focus = str(row.get("Focus", ""))

    numbered_theory_list.append(
        f"{idx+1}. {theory_name}: {explanation} "
        f"Keywords: {keywords}. "
        f"Core Assumption: {core_assumption}. "
        f"Focus: {focus}"
    )

theory_prompt_text = "\n".join(numbered_theory_list)

# =========================
# LLM FONKSİYONU
# =========================

def query_ollama(prompt: str, timeout=TIMEOUT_SECONDS) -> str:
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", MODEL_NAME],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=timeout
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        print("⏰ Timeout! failed olarak işaretlendi.")
        return "failed"
    except Exception as e:
        print("⚠️ Hata oluştu:", e)
        return "failed"

# =========================
# MODEL CEVABI PARSING FONKSİYONU
# =========================

def parse_model_response(response: str) -> int:
    response = response.strip()
    parsing_type = MODEL_PARSING["parsing"]
    phrase = MODEL_PARSING.get("phrase")

    if parsing_type == "start":
        snippet = response[:100]
        match = re.search(r"\b(\d+)\b", snippet)
        if match:
            return int(match.group(1))

    elif parsing_type == "end":
        snippet = response[-100:]  # son 100 karakter
        matches = list(re.finditer(r"\d+", snippet))
        if matches:
            return int(matches[-1].group())

    elif parsing_type == "after" and phrase:
        split_parts = re.split(re.escape(phrase), response, flags=re.IGNORECASE)
        if len(split_parts) > 1:
            after_text = split_parts[1]
            match = re.search(r"\b(\d+)\b", after_text)
            if match:
                return int(match.group(1))

    return None

# =========================
# SINIFLANDIRMA FONKSİYONU
# =========================

def classify_with_llm(title, abstract):

    if abstract.strip():
        text = f"Title: {title}\nAbstract: {abstract}"
    else:
        text = f"Title: {title}"

    prompt = f"""
You are a management research expert.

Select the ONE most appropriate theory from the numbered list below.

Return ONLY the number of the selected theory.
Do not write anything else.
Do not explain.
If none apply, return 0.

Theory List:
{theory_prompt_text}

Article:
{text}
"""

    attempt = 0

    while attempt < MAX_RETRY:
        response = query_ollama(prompt, timeout=TIMEOUT_SECONDS)
        print(response)

        if response == "failed":
            attempt += 1
            print(f"🔁 Timeout veya hata! Retry {attempt}/{MAX_RETRY}")
            time.sleep(2)
            continue

        selected_number = parse_model_response(response)
        if selected_number is None:
            attempt += 1
            print(f"🔁 Sayı parse edilemedi! Retry {attempt}/{MAX_RETRY}")
            time.sleep(2)
            continue

        break
    else:
        return "failed"

    if selected_number == 0:
        return "Other"
    if 1 <= selected_number <= len(df_theories):
        return df_theories.iloc[selected_number - 1]["Theory"]
    else:
        return "Other"

# =========================
# ANA İŞLEM (CHUNKLI + İLERLEME)
# =========================

part_number = 1
processed_count = 0

for chunk in pd.read_csv(INPUT_FILE, chunksize=PART_SIZE):

    if "abstract" not in chunk.columns:
        chunk["abstract"] = ""

    chunk.insert(0, "Core_Theory_Group", "")

    print(f"\n📦 Part {part_number} işleniyor ({len(chunk)} makale)...")

    for i, row in chunk.iterrows():
        title = str(row.get("title", ""))
        abstract = str(row.get("abstract", ""))

        processed_count += 1
        print(f"[{processed_count}/{total_rows}] Classifying...")

        theory = classify_with_llm(title, abstract)
        chunk.at[i, "Core_Theory_Group"] = theory

        time.sleep(1)

    part_filename = f"openalex_part{part_number}.csv"
    chunk.to_csv(part_filename, index=False, encoding="utf-8-sig")
    print(f"💾 {part_filename} kaydedildi.")

    part_number += 1

print("\n✅ Tüm makaleler sınıflandırıldı.")

# =========================
# MERGE İŞLEMİ
# =========================

print("\n🔄 Part dosyaları birleştiriliyor...")

all_parts = sorted(glob.glob("openalex_part*.csv"))

if all_parts:
    merged_df = pd.concat([pd.read_csv(f) for f in all_parts])

    cols = ["Core_Theory_Group"] + [c for c in merged_df.columns if c != "Core_Theory_Group"]
    merged_df = merged_df[cols]

    merged_df.to_csv("openalex_merged.csv", index=False, encoding="utf-8-sig")
    print("✅ Tüm dosyalar birleştirildi: openalex_merged.csv oluşturuldu.")
else:
    print("⚠️ Part dosyası bulunamadı. Birleştirme yapılmadı.")