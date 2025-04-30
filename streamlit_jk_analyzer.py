import streamlit as st
import requests
from bs4 import BeautifulSoup

# Парсинг ЦИАНа (без Playwright)
def parse_cian(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&q={jk_name.replace(' ', '+')}&region=1"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        with st.expander("🔍 Показать HTML"):
            st.code(soup.prettify()[:5000], language="html")

        prices = []
        for tag in soup.find_all("span", {"class": "_93444fe796"}):
            text = tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:  # фильтр по рыночным ценам
                    prices.append(price)

        if not prices:
            st.warning("⚠️ На странице не найдены корректные цены за м²")
            return None

        return {
            "avg": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
            "url": search_url
        }

    except Exception as e:
        st.exception("🛠 Ошибка парсинга")
        return None


# Интерфейс Streamlit
st.title("🏠 Анализ цен на жилые комплексы — Москва")
st.markdown("Введите название ЖК — получите актуальные цены с сайта [Циан](https://www.cian.ru)")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

if jk_name:
    result = parse_cian(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"📊 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} ₽")
        st.write(f"📉 Минимальная цена за м²: {result['min']} ₽")
        st.write(f"📈 Максимальная цена за м²: {result['max']} ₽")
        st.markdown(f"[🔗 Открыть результаты на Циане]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Проверьте написание или попробуйте другой ЖК.")
