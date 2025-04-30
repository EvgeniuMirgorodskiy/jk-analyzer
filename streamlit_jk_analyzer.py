import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time

# Функция парсинга Циан через Playwright
def parse_cian(jk_name):
    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1&q={jk_name.replace(' ', '+')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)
        time.sleep(5)  # Даем время на загрузку JS
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    prices = []
    for price in soup.find_all("span", {"class": "_93444fe796"}):
        try:
            clean_price = int(price.text.replace('\xa0', '').replace('₽', '').strip())
            prices.append(clean_price)
        except ValueError:
            continue

    if prices:
        return {
            "avg": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices)
        }
    else:
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
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Попробуйте уточнить название.")
