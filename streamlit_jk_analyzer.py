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

        # Поиск всех объявлений
        results = soup.find_all("div", {"data-marker": "item"})
        prices = []
        areas = []

        for item in results:
            title_tag = item.find("a", {"data-marker": "title"})
            price_tag = item.find("span", class_="price-root-tm5ut")

            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True).lower()
            price_text = price_tag.get_text(strip=True).replace('\xa0', '').replace(' ', '').strip()

            # Проверяем, подходит ли количество комнат
            if not title.startswith(f"{rooms}-к."):
                continue

            # Извлекаем площадь из заголовка: например, "40 м²"
            area_start = title.find("м²")
            if area_start == -1:
                continue

            area_str = ""
            for i in range(area_start - 1, 0, -1):
                if title[i].isdigit():
                    area_str = title[i] + area_str
                elif area_str:
                    break

            if price_text.isdigit() and area_str:
                total_price = int(price_text)
                area = int(area_str)
                prices.append(total_price)
                areas.append(area)

        # Вычисляем цену за м²
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
        print("Ошибка парсинга:", e)
        return None


# Интерфейс Streamlit
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя цена за м²: {result['avg']:.0f} ₽")
            st.write(f"📉 Минимальная цена: {result['min']} ₽")
            st.write(f"📈 Максимальная цена: {result['max']} ₽")
            st.markdown(f"[🔗 Перейти к объявлениям]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Попробуйте уточнить название ЖК.")
