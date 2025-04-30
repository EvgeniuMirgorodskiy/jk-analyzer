import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}+{rooms}-комнатная"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)
        page.wait_for_selector(".iva-item-content-rejJg iva-item-content-redesign", timeout=10000)  # Ждём загрузки объявлений

        html = page.content()

        soup = BeautifulSoup(html, 'html.parser')

        prices = []
        areas = []

        for item in soup.find_all("div", class_="iva-item-content-rejJg iva-item-content-redesign"):
            price_tag = item.find("span", class_="price-root-_Xp9O")
            area_tag = item.find("span", class_="iva-item-priceStep-GeGDD")

            if price_tag and area_tag:
                price_text = price_tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
                area_text = area_tag.get_text(strip=True).split()[0]

                try:
                    price = int(price_text)
                    area = int(area_text)

                    if 50_000 < price < 500_000:
                        prices.append(price)
                        areas.append(area)
                except ValueError:
                    continue

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


# Интерфейс Streamlit
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if not jk_name.strip():
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя цена за м²: {result['avg']:.0f} ₽")
            st.write(f"📉 Минимальная цена: {result['min']} ₽")
            st.write(f"📈 Максимальная цена: {result['max']} ₽")
            st.markdown(f"[🔗 Перейти к объявлениям]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Попробуйте уточнить название ЖК.")
