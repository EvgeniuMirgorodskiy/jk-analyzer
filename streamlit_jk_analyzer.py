import streamlit as st
import requests
from bs4 import BeautifulSoup


# Функция для парсинга Яндекс.Недвижимости
def parse_yandex_realty(jk_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    }

    # Более точный URL с фильтром "новостройки" и текстовым поиском
    search_url = f"https://realty.ya.ru/moskva/kvartiry/prodam/novostrojki/?text={jk_name.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"❌ Ошибка загрузки страницы: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 💡 Лог: если нужно посмотреть, какой HTML пришёл
        with st.expander("🔍 Посмотреть полученный HTML"):
            st.code(soup.prettify()[:5000], language="html")

        prices = []
        price_tags = soup.find_all("span", {"class": "PriceAndUnit__price"})
        for price_tag in price_tags:
            text = price_tag.get_text(strip=True).replace('\xa0', '').replace('₽', '')
            if text.isdigit():
                price = int(text)
                if 50_000 < price < 500_000:  # Москва: реальные цены за м²
                    prices.append(price)

        if not prices:
            st.warning("⚠️ На странице не найдены подходящие цены")
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
st.title("🏠 Анализ цен на жилые комплексы")
st.markdown("Введите название ЖК в Москве — получите актуальные цены с Яндекс.Недвижимости")

jk_name = st.text_input("🔍 Название ЖК", placeholder="Золотая Миля")

if jk_name:
    with st.spinner("🔎 Ищем данные на Яндекс.Недвижимости..."):
        result = parse_yandex_realty(jk_name)

    if result:
        st.success(f"📈 Статистика по ЖК '{jk_name}'")
        st.write(f"🏠 Найдено предложений: {result['count']}")
        st.write(f"💰 Средняя цена за м²: {result['avg']:.2f} руб.")
        st.write(f"📉 Минимальная цена за м²: {result['min']} руб.")
        st.write(f"📈 Максимальная цена за м²: {result['max']} руб.")
        st.markdown(f"[🔗 Открыть результаты на Яндекс.Недвижимости]({result['url']})")
    else:
        st.warning("❌ По вашему запросу ничего не найдено. Попробуйте более точное название.")
