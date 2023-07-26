from cachetools import cached, TTLCache
from cachetools.keys import hashkey
import asyncio
import nest_asyncio

nest_asyncio.apply()


async def aget(session, urls):
    resp = await session.get(urls)
    return await resp.text()


def key(_, urls):
    return hashkey(urls)


@cached(cache=TTLCache(maxsize=10, ttl=300), key=key)
def get(session, urls):
    loop = asyncio.get_event_loop()
    coroutine = aget(session, urls)
    return loop.run_until_complete(coroutine)
