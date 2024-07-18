#!/usr/bin/env python3
"""
    Create a Cache class
    store an instance of redis client as a private variable named _redis
    and flush the instance using flushdb
"""
import redis
import uuid
from typing import Union, Callable
from functools import wraps, cache


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float, None]:
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Union[int, None]:
        return self.get(key, fn=int)

    def count_calls(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            key = method.__qualname__
            self._redis.incr(key)
            return method(self, *args, **kwargs)
        return wrapper

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def call_history(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            input_key = method.__qualname__ + ":inputs"
            output_key = method.__qualname__ + ":outputs"
            self._redis.rpush(input_key, str(args))
            output = method(self, *args, **kwargs)
            self._redis.rpush(output_key, str(output))
            return output
        return wrapper

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def replay(func):
        method_name = func.__qualname__
        input_key = method_name + ":inputs"
        output_key = method_name + ":outputs"
        inputs = cache._redis.lrange(input_key, 0, -1)
        outputs = cache._redis.lrange(output_key, 0, -1)
        num_calls = len(inputs)
        print(f"{method_name} was called {num_calls} times:")
        for input_data, output_data in zip(inputs, outputs):
            input_args = eval(input_data.decode())
            output_result = eval(output_data.decode())
            print(f"{method_name}(*{input_args}) -> {output_result}")
