import os
import asyncio
import aiohttp
import google.generativeai as genai
import streamlit as st

from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from dotenv import load_dotenv
from scrapper import parse_times_of_india

from typing import List, Dict


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel()

newsapi_client = NewsApiClient(api_key=os.getenv("NEWSAPI_API_KEY"))


def get_articles(query: str = None, sources: str = None, domains: str = None) -> List[Dict]:
    all_articles = newsapi_client.get_everything(q=query,
                                                 sources=sources,
                                                 domains=domains, language='en')['articles']
    return all_articles


def summarize(text: str) -> str:
    prompt = """
    Welcome, News summarizer! Your task is to write a concise, objective summary of this news article in about 100 words, Maintain a neutral tone. Only generate the summary from the information given in the context below.
    """
    response = model.generate_content(prompt + text)
    return response.text


def get_top_3(query: str, sources: str, domains: str) -> List[Dict]:
    all_articles = get_articles(query, sources, domains)
    top_articles = [article for article in all_articles if article['url'].startswith("https://timesofindia.indiatimes.com")][:3]
    return top_articles


async def main():
    st.set_page_config(page_title="News summarizer", layout="wide")
    st.header("Latest news summarizer from timesofindia.com")
    user_query = st.text_input("Enter your query:")
    if user_query:
        all_articles = get_top_3(query=user_query, sources='the-times-of-india', domains='timesofindia.indiatimes.com')
        for article in all_articles:
            response = await parse_times_of_india(article['url'])
            if response is not None:
                st.write(f"### {response['title']}")
                if 'urlToImage' in article and article['urlToImage']:
                    st.image(article['urlToImage'], use_column_width=True)
                st.write(f"Url: [Link]({article['url']})")
                st.write(f"Summary: {summarize(response['content'])}")
                # print(f"Normal content: {response['content']}")


if __name__ == '__main__':
    asyncio.run(main())
