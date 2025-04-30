import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}+{rooms}-комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 🔍 Поиск всех объявлений квартир
        listings = soup.find_all("a", {"data-marker": "title"})

        prices = []
        areas = []

        for listing in listings:
            title = listing.get_text(strip=True).lower()
            href = listing.get("href")
            if str(rooms) in title:
                price_tag = listing.find_next("span", {"data-marker": "item-price"})
                if price_tag:
                    price_text = price_tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
                    area_text = title.split(',')[1].split('м²')[0].strip()  # например: "40&nbsp;"
                    if price_text.isdigit() and area_text.isdigit():
                        price = int(price_text)
                        area = int(area_text)
                        prices.append(price)
                        areas.append(area)

        # 💰 Расчёт цены за м²
        price_per_sqm = [p // a for p, a in zip(prices, areas)]
        valid_prices = [p for p in price_per_sqm if 50_000 < p < 500_000]

        if not valid_prices:
            return None

        return {
            "avg": sum(valid_prices) / len(valid_prices),
            "min": min(valid_prices),
            "max": max(valid_prices),
            "count": len(valid_prices),
            "url": search_url
        }

    except Exception as e:
        print(f"Error parsing Avito: {e}")
        return None


# Интерфейс
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнаты", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if not jk_name.strip():
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя: {result['avg']:.0f} ₽/м²")
            st.write(f"📉 Мин.: {result['min']} ₽/м²")
            st.write(f"📈 Макс.: {result['max']} ₽/м²")
            st.markdown(f"[🔗 Открыть]({result['url']})")
        else:
            st.warning("❌ Ничего не найдено. Попробуйте уточнить название ЖК")
