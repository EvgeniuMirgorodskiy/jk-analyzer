import streamlit as st
import asyncio
import aiohttp
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Новости по недвижимости", layout="wide")
st.title("⚖️💰 Новости: Закон и Инвестиции")

# RSS-каналы
RSS_FEEDS = {
    "РИА Недвижимость": "https://ria.ru/export/rss2/realty.xml",
    "РБК Недвижимость": "https://www.rbc.ru/rbcmoney/rss.rss"
}

# Тематический фильтр
TOPICS = ["все", "закон", "инвестиции"]
topic_filter = st.selectbox("Выберите тему:", options=TOPICS)

# Асинхронная функция для получения новостей
async def fetch_feed(session, url, source_name):
    async with session.get(url, ssl=False, timeout=10) as response:
        if response.status == 200:
            text = await response.text()
            feed = feedparser.parse(text)
            news_list = []
            for i, entry in enumerate(feed.entries):
                if i >= 5:  # Берём только последние 5 статей
                    break
                title = entry.title.lower()
                summary = entry.summary if 'summary' in entry else ""
                link = entry.link
                published = entry.published if 'published' in entry else datetime.now().isoformat()

                news_list.append({
                    "title": entry.title,
                    "summary": summary[:200] + "...",
                    "link": link,
                    "source": source_name,
                    "published": published
                })
            return news_list
    return []

# Параллельная загрузка всех новостей
async def fetch_all_feeds(feeds):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url, name) for name, url in feeds.items()]
        results = await asyncio.gather(*tasks)
        all_news = []
        for result in results:
            all_news.extend(result)
        return all_news

# Кэшируем данные на 3 часа
@st.cache_data(ttl=60 * 60 * 3)
def load_news():
    return asyncio.run(fetch_all_feeds(RSS_FEEDS))

# Загружаем или используем кэш
all_news = load_news()

# Фильтрация по теме
if topic_filter != "все":
    filtered_news = [n for n in all_news if topic_filter in n['title'].lower()]
else:
    filtered_news = all_news

df = pd.DataFrame(filtered_news)
if not df.empty:
    df['published'] = pd.to_datetime(df['published'])
    df = df.sort_values(by='published', ascending=False).reset_index(drop=True)

# Кнопка обновления
if st.button("🔄 Обновить новости"):
    st.cache_data.clear()
    st.experimental_rerun()

# Вывод новостей
st.write(f"Найдено {len(filtered_news)} новостей по теме '{topic_filter}'")

for _, row in df.iterrows():
    st.markdown(f"### [{row['title']}]({row['link']})")
    st.caption(f"Источник: {row['source']} | {row['published'].strftime('%d.%m.%Y %H:%M')}")
    st.write(row['summary'])
    st.divider()

st.sidebar.info("Обновляется автоматически. Последнее обновление: " + str(datetime.now().strftime("%d.%m.%Y %H:%M")))
