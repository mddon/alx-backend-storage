#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker
    obtain the HTML content of a particular URL and returns it """
import redis
import requests



def get_page(url: str) -> str:
    """ track how many times a particular URL was accessed in the key
        "count:{url}"
        and cache the result with an expiration time of 10 seconds """

    redis_conn = redis.Redis()
    count = 0
    redis_conn.set(f"cached:{url}", count)
    response = requests.get(url)
    redis_conn.incr(f"count:{url}")
    redis_conn.setex(f"cached:{url}", 10, redis_conn.get(f"cached:{url}"))
    return response.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
