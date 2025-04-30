import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Точный URL для новостроек в Москве
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}+{rooms}-комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Сохраним HTML для локальной отладки
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        # Парсим цены и площади
        items = soup.find_all("div", {"data-marker": "item"})
        prices = []
        areas = []

        for item in items:
            title_tag = item.find("a", {"data-marker": "title"})
            price_tag = item.find("span", {"data-marker": "price"})

            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True).lower()
            price_text = price_tag.get_text(strip=True).replace(" ", "").replace("\xa0", "")

            # Проверяем, содержит ли заголовок нужное количество комнат
            if f"{rooms}-к. квартира" not in title and f"{rooms}-комнатная" not in title:
                continue

            # Извлекаем цену
            if price_text.isdigit():
                total_price = int(price_text)

                # Ищем площадь в виде "45 м²" внутри заголовка
                area_start = title.find("м²")
                if area_start == -1:
                    continue

                area_str = ""
                for i in range(area_start - 1, 0, -1):
                    if title[i].isdigit():
                        area_str = title[i] + area_str
                    elif area_str:
                        break

                if area_str and area_str.isdigit():
                    area = int(area_str)
                    if area > 10:
                        prices.append(total_price // area)
                        areas.append(area)

        valid_prices = [p for p in prices if 50_000 < p < 500_000]

        if valid_prices:
            return {
                "avg": sum(valid_prices) / len(valid_prices),
                "min": min(valid_prices),
                "max": max(valid_prices),
                "url": search_url,
                "count": len(valid_prices)
            }
        else:
            return None

    except Exception as e:
        print("Ошибка при парсинге:", e)
        return None


# Интерфейс Streamlit
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if not jk_name.strip():
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя цена: {result['avg']:.0f} ₽/м²")
            st.write(f"📉 Мин.: {result['min']} ₽/м²")
            st.write(f"📈 Макс.: {result['max']} ₽/м²")
            st.markdown(f"[🔗 Открыть объявления]({result['url']})")
        else:
            st.warning("❌ Ничего не найдено. Попробуйте другое имя ЖК.")
