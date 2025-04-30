import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Упрощённая ссылка без лишних параметров
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Проверяем заголовок объявлений
        listings = soup.find_all("div", {"data-marker": "item"})

        if not listings:
            with st.expander("🧾 Полученный HTML"):
                st.code(soup.prettify()[:5000], language="html")
            return None

        prices = []
        for item in listings:
            title_tag = item.find("a", {"data-marker": "title"})
            price_tag = item.find("span", class_="price-price-JPjdN")

            if not title_tag or not price_tag:
                continue

            title = title_tag.get_text(strip=True).lower()
            price_text = price_tag.get_text(strip=True).replace('₽', '').replace(' ', '').strip()

            if jk_name.lower() in title and price_text.isdigit():
                price = int(price_text)
                area = 50  # пример площади, можно позже улучшить
                prices.append(price // area)

        valid_prices = [p for p in prices if 50_000 < p < 500_000]
        if valid_prices:
            return {
                "avg": sum(valid_prices) / len(valid_prices),
                "min": min(valid_prices),
                "max": max(valid_prices),
                "count": len(valid_prices),
                "url": search_url
            }
        else:
            return None

    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return None


# Интерфейс Streamlit
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнаты", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name)

        if result:
            st.write(f"💰 Средняя цена за м²: {result['avg']:.0f} ₽")
            st.write(f"📉 Мин.: {result['min']} ₽")
            st.write(f"📈 Макс.: {result['max']} ₽")
            st.markdown(f"[🔗 Открыть объявления]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Попробуйте другое имя ЖК.")
