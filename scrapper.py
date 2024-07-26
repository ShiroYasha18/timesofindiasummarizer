import aiohttp
import certifi
import ssl
from bs4 import BeautifulSoup
from typing import Dict


async def fetch_content(article_url: str):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession() as session:
        async with session.get(article_url, ssl=ssl_context) as response:
            if response.status == 200:
                content = await response.read()
                return content
            else:
                print(f"Error fetching content: {article_url}")
                return None


async def parse_times_of_india(article_url: str) -> Dict[str, str]:
    response = dict()
    content = await fetch_content(article_url)
    if content is None:
        return None

    soup = BeautifulSoup(content, "html.parser")
    content_element = soup.find(attrs={"class": "_s30J clearfix"})

    if content_element is not None:
        response["title"] = soup.find('h1').get_text()
        response["content"] = content_element.get_text()
        return response
    else:
        return None
