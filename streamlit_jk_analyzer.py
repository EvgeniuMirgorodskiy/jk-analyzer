import streamlit as st
import requests
from bs4 import BeautifulSoup

# Функция для парсинга Яндекс.Недвижимости
def parse_yandex_realty(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Поиск квартир в новостройках по ЖК
    search_url = f"https://realty.ya.ru/moskva/kvartiry/prodam/?text={jk_name.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error("❌ Не удалось загрузить страницу")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        prices = []
        for price_tag in soup.find_all("span", {"class": "PriceAndUnit__price"}):
            text = price_tag.get_text(strip=True).replace("\xa0", "").replace("₽", "")
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:  # фильтруем явный мусор
                    prices.append(price)

        if not prices:
            st.warning("⚠️ На странице не найдено корректных цен")
            return None

        return {
            "avg": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
            "url": search_url
        }

    except Exception as e:
        st.error(f"Ошибка при парсинге: {e}")
        return None


# Интерфейс Streamlit
st.title("📊 Анализ цен на жилые комплексы")
st.markdown("Введите название ЖК в Москве — получите актуальные цены с Яндекс.Недвижимости.")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

if jk_name:
    with st.spinner("🔎 Соверькинопкастаоткаруж4. Унильза текст
