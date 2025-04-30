import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_yandex_realty(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Search URL for new builds in Moscow with text query
    search_url = f"https://realty.ya.ru/moskva/kvartiry/prodam/novostrojki/?text={jk_name.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"❌ Error fetching page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # For debugging: show first part of the HTML
        with st.expander("🔍 Show raw HTML"):
            st.code(soup.prettify()[:5000], language='html')

        prices = []
        price_tags = soup.find_all("span", {"class": "PriceAndUnit__price"})
        for tag in price_tags:
            text = tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:  # Filter out unrealistic prices
                    prices.append(price)

        if not prices:
            st.warning("⚠️ No valid prices found")
            return None

        return {
            "avg": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
            "url": search_url
        }

    except Exception as e:
        st.exception("Parsing error")
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
