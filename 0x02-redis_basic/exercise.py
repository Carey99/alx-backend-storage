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

    def replay(fn: Callable) -> None:
        '''Displays the call history of a Cache class' method.
        '''
        if fn is None or not hasattr(fn, '__self__'):
            return
        redis_store = getattr(fn.__self__, '_redis', None)
        if not isinstance(redis_store, redis.Redis):
            return
        fxn_name = fn.__qualname__
        in_key = '{}:inputs'.format(fxn_name)
        out_key = '{}:outputs'.format(fxn_name)
        fxn_call_count = 0
        if redis_store.exists(fxn_name) != 0:
            fxn_call_count = int(redis_store.get(fxn_name))
        print('{} was called {} times:'.format(fxn_name, fxn_call_count))
        fxn_inputs = redis_store.lrange(in_key, 0, -1)
        fxn_outputs = redis_store.lrange(out_key, 0, -1)
        for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
            print('{}(*{}) -> {}'.format(
                fxn_name,
                fxn_input.decode("utf-8"),
                fxn_output,
            ))
