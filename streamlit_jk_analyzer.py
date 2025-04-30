import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Функция парсинга базы ЦИАН по названию ЖК
def parse_cian(jk_name):
    # Пример страницы поиска ЖК
    search_url = f"https://www.cian.ru/baza-cian/zhiloy-kompleks/?text={jk_name}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Проверяем, есть ли элементы с ценами
        price_elements = soup.find_all("div", {"data-name": "Price"})
        if not price_elements:
            return None

        prices = []
        for el in price_elements:
            try:
                text = el.get_text(strip=True).replace('₽', '').replace('\xa0', '')
                if '—' in text:  # если диапазон
                    parts = text.split('—')
                    avg = (int(parts[0]) + int(parts[1])) / 2
                    prices.append(avg)
                else:
                    prices.append(int(text))
            except Exception as e:
                continue

        if not prices:
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
st.markdown("Введите название ЖК в Москве — получите актуальные цены с сайта ЦИАН.")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Лесные поляны")

if jk_name:
    with st.spinner("🔎 Ищем данные на ЦИАН..."):
        result = parse_cian(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"🏠 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} руб.")
        st.write(f"📉 Минимальная цена за м²: {result['min']} руб.")
        st.write(f"📈 Максимальная цена за м²: {result['max']} руб.")
        st.markdown(f"[🔗 Перейти к результату на ЦИАН]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Попробуйте уточнить название.")
