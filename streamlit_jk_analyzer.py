import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Точный URL по ЖК и количеству комнат
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}+{rooms}-комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Сохраним HTML для отладки
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        # Это тестовые данные, пока парсер не работает
        test_prices = [120000, 125000, 130000, 110000, 115000]

        return {
            "avg": sum(test_prices) / len(test_prices),
            "min": min(test_prices),
            "max": max(test_prices),
            "url": search_url,
            "test_data_used": True
        }

    except Exception:
        return None


# Интерфейс
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            if result.get('test_data_used'):
                st.info("ℹ️ Выведены тестовые цены — парсер всё ещё не находит реальных данных")
            st.write(f"💰 Средняя: {result['avg']:.0f} ₽")
            st.write(f"📉 Мин.: {result['min']} ₽")
            st.write(f"📈 Макс.: {result['max']} ₽")
            st.markdown(f"[🔗 Открыть]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Проверьте debug.html")
