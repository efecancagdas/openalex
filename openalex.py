import requests
import pandas as pd
import time

EMAIL = "haydar.yalcin@gmail.com"
BASE_URL = "https://api.openalex.org/works"
PER_PAGE = 200
MAX_RECORDS = 10000

QUERY = """
("small and medium enterprise" OR SME OR "small business")
AND ("digital transformation" OR digitalization OR digitization)
AND ("strategic agility" OR agility)
AND ("organizational resilience" OR resilience)
"""

FILTERS = "type:article,language:en,from_publication_date:2000-01-01"


# 🔹 Abstract'i inverted index'ten düz metin olarak al
def get_abstract(work):
    inverted_index = work.get("abstract_inverted_index")
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()  # pozisyona göre sırala
    abstract_text = " ".join([w for pos, w in word_positions])
    return abstract_text


def fetch_limited_metadata():
    cursor = "*"
    total_fetched = 0
    all_records = []

    params = {
        "search": QUERY,
        "filter": FILTERS,
        "per-page": PER_PAGE,
        "cursor": cursor,
        "mailto": EMAIL
    }

    # 🔹 İlk istek → toplam yayın sayısını öğren
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    total_count = data.get("meta", {}).get("count", 0)
    print(f"\n📊 Toplam yayın sayısı (OpenAlex): {total_count}")
    print(f"📥 Maksimum indirilecek yayın: {MAX_RECORDS}\n")

    while total_fetched < MAX_RECORDS:
        params["cursor"] = cursor
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        results = data.get("results", [])

        if not results:
            break

        remaining_quota = MAX_RECORDS - total_fetched
        results = results[:remaining_quota]

        all_records.extend(results)
        total_fetched += len(results)

        print(f"✔ Çekilen: {total_fetched} / {MAX_RECORDS}")

        if total_fetched >= MAX_RECORDS:
            break

        cursor = data.get("meta", {}).get("next_cursor")

        if not cursor:
            break

        time.sleep(1)  # polite delay

    print("\n✅ İndirme tamamlandı.")
    return all_records


def clean_records(records):
    cleaned_data = []

    for work in records:
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        journal_name = source.get("display_name")

        authors = "; ".join(
            [
                a["author"]["display_name"]
                for a in work.get("authorships", [])
                if a.get("author")
            ]
        )

        institutions = "; ".join(
            [
                inst["display_name"]
                for a in work.get("authorships", [])
                for inst in (a.get("institutions") or [])
                if inst.get("display_name")
            ]
        )

        abstract_text = get_abstract(work)

        cleaned_data.append({
            "title": work.get("display_name"),
            "abstract": abstract_text,               # ← Abstract eklendi
            "publication_year": work.get("publication_year"),
            "publication_date": work.get("publication_date"),
            "journal": journal_name,
            "doi": work.get("doi"),
            "cited_by_count": work.get("cited_by_count"),
            "authors": authors,
            "institutions": institutions,
            "openalex_id": work.get("id")
        })

    return cleaned_data


# =========================
# 🔹 ÇALIŞTIR
# =========================

records = fetch_limited_metadata()

print("\n🔄 Veriler temizleniyor...")
cleaned = clean_records(records)

print("💾 CSV dosyası oluşturuluyor...")
df = pd.DataFrame(cleaned)
df.to_csv("openalex_limited.csv", index=False, encoding="utf-8-sig")

print("\n🎉 İşlem tamamlandı!")
print("📁 Dosya adı: openalex_limited.csv")