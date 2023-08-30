from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from django.conf import settings
from requests.models import PreparedRequest


def key(_, urls):
    return hashkey(urls)


@cached(cache=TTLCache(maxsize=10, ttl=300), key=key)
def get(session, urls):
    response = session.get(urls)
    return response.text


def use_proxy(driver, destination, genre):
    if not settings.PROXY_ADDRESS:
        return destination

    params = {"destination": destination, "driver": driver, "genre": genre}

    req = PreparedRequest()
    req.prepare_url(settings.PROXY_ADDRESS, params)

    return req.url
