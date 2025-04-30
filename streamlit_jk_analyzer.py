from playwright.sync_api import sync_playwright
import streamlit as st
from bs4 import BeautifulSoup
import requests

def parse_cian_with_playwright(jk_name):
    url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&q={jk_name.replace(' ', '+')}&region=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)  # ждём подгрузки JS
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    with st.expander("🔍 Показать HTML"):
        st.code(soup.prettify()[:2000], language="html")

    prices = []
    for price_tag in soup.find_all("span", {"class": "_93444fe796"}):
        try:
            text = price_tag.get_text(strip=True).replace("\xa0", "").replace("₽", "")
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:
                    prices.append(price)
        except:
            continue

    if prices:
        return {
            "avg": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
            "url": url
        }
    else:
        return None


# Интерфейс Streamlit
st.title("🏠 Анализ цен на жилые комплексы — Москва")
st.markdown("Введите название жилого комплекса — получите актуальные цены с сайта [Циан](https://www.cian.ru)")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

if jk_name:
    result = parse_cian_with_playwright(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"📊 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} ₽")
        st.write(f"📉 Минимальная цена за м²: {result['min']} ₽")
        st.write(f"📈 Максимальная цена за м²: {result['max']} ₽")
        st.markdown(f"[🔗 Открыть результаты на Циан]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Проверьте, есть ли объявления на сайте.")
