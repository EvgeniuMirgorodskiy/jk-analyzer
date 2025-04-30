import streamlit as st
import feedparser
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Новости Недвижимости", layout="wide")
st.title("📰 Актуальные новости по недвижимости")

# Источники
RSS_FEEDS = {
    "РИА Недвижимость": "https://ria.ru/export/rss2/realty.xml",
    "Яндекс.Новости — Недвижимость": "https://news.yandex.ru/realty.rss",
    "РБК Недвижимость": "https://www.rbc.ru/rbcmoney/rss.rss"
}

# Тематический фильтр
TOPICS = ["все", "цены", "рынок", "инвестиции", "строительство", "закон"]

topic_filter = st.selectbox("Выберите тему:", options=TOPICS)

# Парсер
@st.cache_data(ttl=60*60)  # кэшируем на 1 час
def fetch_news(feed_url):
    feed = feedparser.parse(feed_url)
    news_list = []
    for entry in feed.entries:
        title = entry.title.lower()
        summary = entry.summary if 'summary' in entry else ""
        link = entry.link
        published = entry.published if 'published' in entry else datetime.now().isoformat()
        source = feed.feed.title

        news_list.append({
            "title": entry.title,
            "summary": summary,
            "link": link,
            "source": source,
            "published": published
        })
    return news_list

# Сбор всех новостей
all_news = []
for source, url in RSS_FEEDS.items():
    all_news.extend(fetch_news(url))

# Фильтрация по теме
if topic_filter != "все":
    filtered_news = [n for n in all_news if topic_filter in n['title'].lower()]
else:
    filtered_news = all_news

# Сортировка по дате
df = pd.DataFrame(filtered_news)
df['published'] = pd.to_datetime(df['published'])
df = df.sort_values(by='published', ascending=False).reset_index(drop=True)

# Вывод
st.write(f"Найдено {len(filtered_news)} новостей по теме '{topic_filter}'")

for i, row in df.iterrows():
    st.markdown(f"### [{row['title']}]({row['link']})")
    st.caption(f"Источник: {row['source']} | {row['published'].strftime('%d.%m.%Y %H:%M')}")
    st.write(row['summary'][:250] + "...")  # Краткое содержание
    st.divider()

st.sidebar.info("Обновляется автоматически. Последнее обновление: " + str(datetime.now().strftime("%d.%m.%Y %H:%M")))
