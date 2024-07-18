#!/usr/bin/env python3
"""
Task: Working with Redis
"""
import redis
import requests
from functools import wraps
from typing import Callable
from datetime import datetime

# Create a Redis client
redis_client = redis.Redis()

def get_page(url: str) -> str:
    # Check if the URL is already cached
    cached_content = redis_client.get(url)
    if cached_content:
        return cached_content.decode()

    # Make the request to the URL
    response = requests.get(url)
    content = response.text

    # Cache the content with an expiration time of 10 seconds
    redis_client.setex(url, 10, content)

    return content
