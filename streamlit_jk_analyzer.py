import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Функция парсинга базы ЦИАН по названию ЖК
def parse_cian(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1&q={jk_name.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"Ошибка загрузки страницы: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 📌 Только элементы с ценой за м²
        prices = []
        for tag in soup.find_all(['span', 'div', 'p']):
            text = tag.get_text(strip=True)
            if not text:
                continue

            # Ищем только если есть "₽/м²" или "руб./м²"
            if '/м²' in text and any(char.isdigit() for char in text):
                try:
                    # Оставляем только цифры
                    price_text = ''.join(filter(str.isdigit, text.split(' ')[0]))
                    if price_text:
                        price_value = int(price_text)

                        # Исключаем явно неправильные значения
                        if 30_000 < price_value < 500_000:  # реальный диапазон для Москвы
                            prices.append(price_value)
                except Exception as e:
                    continue

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
