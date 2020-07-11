from functools import wraps
from time import sleep
from typing import Union, Iterable


def retry(
        exceptions: Union[Exception, Iterable[Exception]], tries=4, delay=3, backoff=2,
        default=None):
    """
    Retry calling the decorated function using an exponential backoff.
    :param exceptions: an exception (or iterable) to check  of exceptions)
    :param logger: <Callable> logger to use ('print' by default)
    :param tries: <int> number of times to try (not retry) before giving up
    :param delay: <int, float> initial delay between retries in seconds
    :param backoff: <int, float> backoff multiplier. For example, backoff=2 will make the delay x2 for each retry
    """
    exceptions = (exceptions, ) if not isinstance(exceptions, tuple) else exceptions

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            f_tries, f_delay = tries, delay
            while f_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    msg = f"{str(e)}, Retrying in {f_delay} seconds. fn: {f.__name__}\nargs: {args},\nkwargs: {kwargs}"
                    sleep(f_delay)
                    f_tries -= 1
                    f_delay *= backoff
            return default if default is not None else f(*args, **kwargs)
        return f_retry
    return deco_retry

