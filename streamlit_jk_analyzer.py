import streamlit as st
import requests
from bs4 import BeautifulSoup


def parse_cian(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    search_url = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&q={jk_name.replace(' ', '+')}&region=1"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            st.error(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 🔍 Отладка: покажем полный HTML, чтобы проверить, есть ли цены
        with st.expander("🧾 Полученный HTML"):
            st.code(soup.prettify(), language="html")

        prices = []
        price_tags = soup.find_all("span", {"class": "_93444fe796"})
        for tag in price_tags:
            text = tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:
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
            st.warning("⚠️ На странице не найдены корректные цены")
            return None

    except Exception as e:
        st.exception("🛠 Ошибка при парсинге")
        return None

# UI
st.title("🏠 Анализ цен на жилые комплексы — Москва")
st.markdown("Введите название ЖК — получите среднюю цену за м² с сайта [Циан](https://www.cian.ru)")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Например: Золотая Миля")

if jk_name:
    with st.spinner("🔎 Ищем данные на Циане..."):
        result = parse_cian(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"📊 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} ₽")
        st.write(f"📉 Минимальная цена за м²: {result['min']} ₽")
        st.write(f"📈 Максимальная цена за м²: {result['max']} ₽")
        st.markdown(f"[🔗 Открыть объявления]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Проверьте написание или попробуйте другой ЖК.")
