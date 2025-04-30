import streamlit as st
import pandas as pd
from io import StringIO
import requests
from bs4 import BeautifulSoup
import time

# Парсер ЦИАН
def parse_cian_prices(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1&q={jk_name.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Проверка: получили ли мы нормальную страницу, а не бан
        if len(soup.text) < 1000:
            st.warning("⚠️ Получена короткая страница — возможно, сработала защита от парсинга")
            return None

        prices = []
        for price in soup.find_all("span", {"class": "_93444fe796"}):
            clean_price = int(price.text.replace('\xa0', '').replace('₽', '').strip())
            prices.append(clean_price)

        if not prices:
            return None

        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        return {
            "avg": avg_price,
            "min": min_price,
            "max": max_price,
            "count": len(prices)
        }

    except Exception as e:
        st.error(f"Ошибка при парсинге: {e}")
        return None


# Интерфейс
st.title("📊 Анализ цен на жилые комплексы")
st.markdown("Введите название ЖК в Москве — получите анализ цен с сайта ЦИАН.")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Лесные поляны")

if jk_name:
    with st.spinner("🔎 Ищем данные на ЦИАН..."):
        result = parse_cian_prices(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"🏠 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} руб.")
        st.write(f"📉 Минимальная цена за м²: {result['min']} руб.")
        st.write(f"📈 Максимальная цена за м²: {result['max']} руб.")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Попробуйте уточнить название.")
