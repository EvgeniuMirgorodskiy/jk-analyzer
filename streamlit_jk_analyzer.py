import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Точный URL по ЖК и количеству комнат
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name} {rooms}-комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 💡 Выведем HTML для отладки
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        price_tags = soup.find_all("meta", {"itemprop": "price"})
        area_tags = soup.find_all("span", class_="style-item-address__string-wZ1xJ")

        prices = []
        areas = []

        for tag in price_tags:
            content = tag.get("content")
            if content and content.isdigit():
                prices.append(int(content))

        for tag in area_tags:
            text = tag.get_text(strip=True)
            if "м²" in text:
                area = text.split("м²")[0].split(",")[-1]
                if area.strip().isdigit():
                    areas.append(int(area.strip()))

        # Если нет данных
        if not price_tags or not area_tags:
            st.warning("⚠️ Нет данных в HTML")
            return None

        # Вычисляем цену за м²
        price_per_sqm = [p // int(areas[i % len(areas)]) for i, p in enumerate(prices)]
        filtered_prices = [p for p in price_per_sqm if 50_000 < p < 500_000]

        if not filtered_prices:
            return None

        return {
            "avg": sum(filtered_prices) / len(filtered_prices),
            "min": min(filtered_prices),
            "max": max(filtered_prices),
            "url": search_url
        }

    except Exception as e:
        st.exception("🛠 Ошибка при парсинге")
        return None


# Интерфейс
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнаты", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя: {result['avg']:.0f} ₽")
            st.write(f"📉 Мин.: {result['min']} ₽")
            st.write(f"📈 Макс.: {result['max']} ₽")
            st.markdown(f"[🔗 Открыть]({result['url']})")
        else:
            st.warning("❌ Ничего не найдено. Попробуйте изменить имя или проверить debug.html")
