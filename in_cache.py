import requests
import requests_cache


def get_from_cache(*args, **kwargs):
    """If the request is already in the cache, return it, otherwise return None."""
    prepared_request = _prepare(*args, **kwargs)
    cache_hash = get_hash(prepared_request)
    response, timestamp = requests_cache.get_response_and_time(cache_hash)
    if response is not None:
        # decorate response like requests_cache
        response.from_cache = True
        response.cache_date = timestamp
    return response  # even if it's None.


def get_hash(prepared_request):
    """call requests_cache caching function."""
    # TODO: this should use whatever requests_cache is currently monkeypatching
    # into requests. Not sure how to find that out. In practice, all backends
    # use BaseCache's implementation.
    return requests_cache.backends.base.BaseCache().create_key(prepared_request)


def _prepare(*args, **kwargs):
    return requests.Request(*args, **kwargs).prepare()


def test_hash():
    known_hash = "90fb40969ef2176b7554da247c437af9b68b2f668e344986fd1fd007e4ee9874"
    evaluated_hash = get_hash(_prepare("POST", "http://httpbin.org/post"))
    assert evaluated_hash == known_hash


def test_cache():
    nuke_cache()
    configure_cache()
    run1 = get_from_cache()
    assert run1 is None
    get_page_from_internet()
    run2 = get_from_cache()
    assert looks_okay(run2)
