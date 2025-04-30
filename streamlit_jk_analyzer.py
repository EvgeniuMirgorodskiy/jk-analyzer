import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Ссылка для поиска по ЖК и количеству комнат
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojka?cd=1&q={jk_name}+{rooms}+комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск цен
        prices = []
        price_tags = soup.find_all("meta", {"itemprop": "price"})
        for tag in price_tags:
            price_str = tag.get("content")
            if price_str and price_str.isdigit():
                price = int(price_str)
                if 1_000_000 < price < 30_000_000:  # фильтр по рыночным ценам в Москве
                    prices.append(price)

        if prices:
            return {
                "avg": sum(prices) / len(prices),
                "min": min(prices),
                "max": max(prices),
                "count": len(prices),
                "url": search_url
            }
        else:
            st.warning("⚠️ На странице не найдено корректных цен")
            return None

    except Exception as e:
        st.exception("🛠 Произошла ошибка при парсинге")
        return None


# Интерфейс Streamlit
st.set_page_config(page_title="Недвижимость Москвы", layout="centered")

st.title("🏠 Недвижимость Москвы")
st.markdown("Введите название жилого комплекса и выберите количество комнат — получите актуальные цены с сайта [Avito](https://www.avito.ru)")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

room_options = ["1 комната", "2 комнаты", "3 комнаты", "4 комнаты", "5 комнат"]
selected_room = st.selectbox("🧱 Количество комнат", room_options)

if st.button("🔎 Найти цены"):
    if not jk_name.strip():
        st.error("🚨 Укажите название ЖК")
    else:
        with st.spinner("🔎 Запрашиваем данные с Avito..."):
            result = parse_avito(jk_name, selected_room[0])

        if result:
            st.success(f"📈 Статистика по ЖК '{jk_name}' ({selected_room})")
            st.write(f"📊 Найдено предложений: {result['count']}")
            st.write(f"💰 Средняя цена: {result['avg']:,} ₽".replace(",", " "))
            st.write(f"📉 Минимальная цена: {result['min']:,} ₽".replace(",", " "))
            st.write(f"📈 Максимальная цена: {result['max']:,} ₽".replace(",", " "))
            st.markdown(f"[🔗 Открыть объявления]({result['url']})")
