import os
import asyncio
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from newsapi import NewsApiClient
from dotenv import load_dotenv
from scrapper import parse_times_of_india
from typing import List, Dict

# Load environment variables
load_dotenv()

# Configure the generative model with Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel()

# Configure the NewsAPI client
newsapi_client = NewsApiClient(api_key=os.getenv("NEWSAPI_API_KEY"))

# Initialize FastAPI
app = FastAPI()

def get_articles(query: str = None, sources: str = None, domains: str = None) -> List[Dict]:
    all_articles = newsapi_client.get_everything(q=query,
                                                 sources=sources,
                                                 domains=domains,
                                                 language='en')['articles']
    return all_articles

def summarize(text: str) -> str:
    prompt = """
    Welcome, News summarizer! Your task is to write a concise, objective summary of this news article in about 100 words. Maintain a neutral tone. Only generate the summary from the information given in the context below.
    """
    response = model.generate_content(prompt + text)
    print(response)  # Print the entire response object to see its structure
    return "Summarization failed due to structure issue."


def get_top_3(query: str, sources: str, domains: str) -> List[Dict]:
    all_articles = get_articles(query, sources, domains)
    top_articles = [article for article in all_articles if article['url'].startswith("https://timesofindia.indiatimes.com")][:3]
    return top_articles
@app.get("/")
def read_root():
    return {"message": "Welcome to the News Summarizer API"}
@app.get("/summarize_news/")
async def summarize_news(query: str = Query(...)) -> JSONResponse:
    articles_data = []
    all_articles = get_top_3(query=query, sources='the-times-of-india', domains='timesofindia.indiatimes.com')
    for article in all_articles:
        response = await parse_times_of_india(article['url'])
        if response is not None:
            summarized_text = summarize(response['content'])
            articles_data.append({
                "title": response['title'],
                "url": article['url'],
                "image_url": article.get('urlToImage', None),
                "summary": summarized_text
            })
    return JSONResponse(content={"articles": articles_data})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
