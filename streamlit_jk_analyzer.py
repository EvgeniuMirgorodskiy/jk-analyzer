import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_avito(jk_name, rooms):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    search_url = f"https://www.avito.ru/moskva/kvartiry/prodam/novostrojki?q={jk_name}+{rooms}-комнатная"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Парсим цены
        price_tags = soup.find_all("span", {"class": "price-root-tm5ut"})
        area_tags = soup.find_all("div", {"class": "geo-georeferences_Yqjte"})

        prices = []
        areas = []

        for tag in price_tags:
            text = tag.get_text(strip=True).replace('\xa0', '').replace(' ', '').replace('\u2009', '')
            if text.isdigit():
                prices.append(int(text))

        for tag in area_tags:
            text = tag.get_text(strip=True)
            if "м²" in text:
                area_str = ''.join(filter(str.isdigit, text.split(',')[1]))
                if area_str:
                    areas.append(int(area_str))

        # Проверяем совпадения по количеству комнат
        title_tags = soup.find_all("h3", {"class": "styles-module-root-PY1ie styles-module-size_l-OXwVr"})
        titles = [tag.get_text(strip=True).lower() for tag in title_tags]

        valid_price_area = []
        for i in range(min(len(prices), len(areas))):
            title = titles[i] if i < len(titles) else ""
            if str(rooms) in title and "комн." in title or "комнатная" in title:
                price = prices[i]
                area = areas[i]
                valid_price_area.append(price // area)

        if not valid_price_area:
            return None

        return {
            "avg": sum(valid_price_area) / len(valid_price_area),
            "min": min(valid_price_area),
            "max": max(valid_price_area),
            "url": search_url
        }

    except Exception as e:
        print(f"Error parsing Avito: {e}")
        return None


# Интерфейс Streamlit
st.title("🏠 Недвижимость Москвы")

jk_name = st.text_input("ЖК")
rooms = st.selectbox("Комнат", ["1", "2", "3", "4", "5"])

if st.button("🔎 Найти"):
    if jk_name.strip() == "":
        st.error("⚠️ Введите название ЖК")
    else:
        result = parse_avito(jk_name, rooms)

        if result:
            st.write(f"💰 Средняя цена за м²: {result['avg']:.0f} ₽")
            st.write(f"📉 Мин.: {result['min']} ₽")
            st.write(f"📈 Макс.: {result['max']} ₽")
            st.markdown(f"[🔗 Перейти к объявлениям]({result['url']})")
        else:
            st.warning("❌ По вашему запросу ничего не найдено. Попробуйте изменить имя ЖК.")
