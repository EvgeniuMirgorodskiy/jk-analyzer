import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Более простой и стабильный URL для тестирования
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        price_tags = soup.find_all("meta", {"itemprop": "price"})
        area_tags = soup.find_all("span", {"data-marker": "square"})

        prices = []
        areas = []

        for tag in price_tags:
            if tag.get("content") and tag.get("content").isdigit():
                prices.append(int(tag.get("content")))

        for tag in area_tags:
            text = tag.get_text(strip=True).split(',')[0].replace('м²', '').strip()
            if text.isdigit():
                areas.append(int(text))

        # Простое совпадение по количеству — не всегда точное, но даст общее представление
        if len(prices) == len(areas):
            price_per_sqm = [p // a for p, a in zip(prices, areas)]
        else:
            avg_price = sum(prices) // len(prices)
            avg_area = sum(areas) // len(areas)
            price_per_sqm = [avg_price // avg_area]

        filtered_prices = [p for p in price_per_sqm if 50_000 < p < 500_000]

        if not filtered_prices:
            return None

        return {
            "avg": sum(filtered_prices) / len(filtered_prices),
            "min": min(filtered_prices),
            "max": max(filtered_prices),
            "url": search_url
        }

    except Exception:
        return None


# Интерфейс
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("Название ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя цена за м²: {result['avg']:.0f} ₽")
            st.write(f"📉 Минимальная цена за м²: {result['min']:.0f} ₽")
            st.write(f"📈 Максимальная цена за м²: {result['max']:.0f} ₽")
            st.markdown(f"[🔗 Открыть объявления]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Проверьте написание названия.")
