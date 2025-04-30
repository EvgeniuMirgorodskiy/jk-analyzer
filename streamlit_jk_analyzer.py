from playwright.sync_api import sync_playwright
import streamlit as st
from bs4 import BeautifulSoup


def parse_cian_with_playwright(jk_name):
    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&q={jk_name}&region=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)
        page.wait_for_timeout(10000)  # ждём подгрузки JS
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    # Показываем HTML для проверки
    with st.expander("🔍 Show raw HTML"):
        st.code(soup.prettify()[:5000], language="html")

    prices = []
    for tag in soup.find_all("span", {"class": "_93444fe796"}):
        text = tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
        if text.isdigit():
            price = int(text)
            if 50_000 < price < 500_000:  # фильтр по рыночным ценам в Москве
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
        return None


# Streamlit UI
st.title("🏠 Анализ цен на ЖК — Москва")
st.markdown("Введите название ЖК — получите среднюю цену за м² с сайта Циан")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

if jk_name:
    with st.spinner("🔎 Ищем данные на Циане..."):
        result = parse_cian_with_playwright(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"📊 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} ₽")
        st.write(f"📉 Минимальная цена за м²: {result['min']} ₽")
        st.write(f"📈 Максимальная цена за м²: {result['max']} ₽")
        st.markdown(f"[🔗 Открыть результаты на Циан]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Попробуйте более точное название или проверьте HTML вывод.")
