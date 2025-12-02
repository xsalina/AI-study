import aiohttp
import asyncio
import certifi
import ssl
from bs4 import BeautifulSoup

ssl_context = ssl.create_default_context(cafile=certifi.where())

SEM_LIMIT = 5


async def getTitles(session, url, sem):
    async with sem:
        try:
            async with session.get(url, ssl=ssl_context) as response:
                if response.status != 200:
                    return {"url": url, "error": f"HTTP {response.status}"}
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    return {"url": url, "title": title_tag.text.strip()}
                return {"url": url, "title": "NO <title> found"}
        except asyncio.TimeoutError:
            return {"url": url, "error": "timeout"}
        except aiohttp.ClientError as e:
            return {"url": url, "error": f"Client {str(e)}"}
        except Exception as e:
            return {"url": url, "error": f"Exception {str(e)}"}


async def fetch_all_titles(urls):
    sem = asyncio.Semaphore(SEM_LIMIT)
    async with aiohttp.ClientSession(headers={
        "User-Agent": "Mozilla/5.0 (async crawler)"
    }) as session:
        tasks = [getTitles(session, url, sem) for url in urls]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.google.com",
        "https://www.github.com",
        "https://thisurldoesnotexist.foo"
    ]
    results = asyncio.run(fetch_all_titles(urls))
    for item in results:
        print(item)
