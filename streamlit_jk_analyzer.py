from playwright.sync_api import sync_playwright
import streamlit as st
from bs4 import BeautifulSoup

def parse_cian_with_playwright(jk_name):
    url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&q={jk_name}&region=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)  # ждём JS
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    with st.expander("🔍 Raw HTML from CIAN"):
        st.code(soup.prettify()[:2000], language="html")

    prices = []
    for price in soup.find_all("span", {"class": "_93444fe796"}):
        try:
            clean_price = int(price.text.replace("\xa0", "").replace("₽", "").strip())
            if 50_000 < clean_price < 500_000:
                prices.append(clean_price)
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


st.title("🏠 Real Estate Price Analyzer — Moscow New Buildings")
st.markdown("Enter a residential complex (JK) name and get average prices per m²")

jk_name = st.text_input("🔍 Enter JK Name", placeholder="Example: Золотая Миля / Zolotaya Milya")

if jk_name:
    result = parse_yandex_realty(jk_name)

    if result:
        st.success(f"📈 Stats for '{jk_name}'")
        st.write(f"📊 Found entries: {result['count']}")
        st.write(f"💰 Average price per m²: {result['avg']:.2f} ₽")
        st.write(f"📉 Min price per m²: {result['min']} ₽")
        st.write(f"📈 Max price per m²: {result['max']} ₽")
        st.markdown(f"[🔗 Open results on Ya.Realty]({result['url']})")
    else:
        st.warning("❌ Nothing found. Try to specify the name or check the HTML output")
