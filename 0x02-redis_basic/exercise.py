import redis
import uuid
from typing import Union, Callable, Optional

def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a particular function."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapped function."""
        key = f"{method.__qualname__}:inputs"
        self._redis.rpush(key, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(f"{method.__qualname__}:outputs", str(data))
        return data
    return wrapper

def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times methods of the Cache class are called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapped function."""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

class Cache:
    """Cache class for interacting with Redis."""
    def __init__(self):
        """Initialize the Cache instance."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generate a random key using uuid, store the input data in Redis, and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """Retrieve data from Redis using the specified key."""
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Retrieve data from Redis as a string."""
        return self._redis.get(key).decode("utf-8")

    def get_int(self, key: str) -> int:
        """Retrieve data from Redis as an integer."""
        data = self._redis.get(key)
        return int(data.decode("utf-8")) if data else 0

def replay(method: Callable):
    """Display the history of calls of a particular function."""
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"
    redis = method.__self__._redis
    count = redis.get(key).decode("utf-8")
    print("{} was called {} times:".format(key, count))
    input_list = redis.lrange(inputs, 0, -1)
    output_list = redis.lrange(outputs, 0, -1)
    for inp, out in zip(input_list, output_list):
        print("{}(*{}) -> {}".format(key, inp.decode("utf-8"), out.decode("utf-8")))
