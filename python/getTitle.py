import asyncio
import aiohttp
from bs4 import BeautifulSoup

SEM_LIMIT = 5
async def getTitleByhttps(session,url,sem):
    # 爬去单个网页的标题
    async with sem:
        try:
            async with session.get(url,timeout=10) as response:
                if response.status != 200:
                    return {"url":url,"error":f"HTTP {response.status}"}
                html = await response.text()
                soup = BeautifulSoup(html,'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    return {"url":url,"title":title_tag.text.strip()}
                else:
                    return {"url":url,"title":"NO <title> find"}

        except asyncio.TimeoutError:
            return {"url":url,"error":'Timeout'}
        except aiohttp.ClientError as e:
            return {"url":url,"error":f"Clinet error: {str(e)}"}
        except Exception as e:
            return {"url":url,"error":f"Unknown error: {str(e)}"}


async def fetch_all_title(urls):
    sem = asyncio.Semaphore(SEM_LIMIT)

    async with aiohttp.ClientSession(headers={
        "User-Agent":"Mozilla/5.0 (async crawler)"
    }) as session:
        tasks = [getTitleByhttps(session,url,sem) for url in urls]
        # gather接受一个一个独立的参数，*表示解析了数组
        return await asyncio.gather(*tasks)

if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.google.com",
        "https://www.github.com",
        "https://thisurldoesnotexist.foo"
    ]
    results = asyncio.run(fetch_all_title(urls))
    for item in results:
        print(item)















        
    