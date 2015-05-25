import ast
import functools
import inspect
import os
import six
import time
from base64 import b64decode, b64encode
from binascii import hexlify

import ujson as json  # NOQA
from cornice import cors
from colander import null


def strip_whitespace(v):
    """Remove whitespace, newlines, and tabs from the beginning/end
    of a string.

    :param str v: the string to strip.
    :rtype: str
    """
    return v.strip(' \t\n\r') if v is not null else v


def msec_time():
    """Return current epoch time in milliseconds.

    :rtype: int
    """
    return int(time.time() * 1000.0)  # floor


def classname(obj):
    """Get a classname from an object.

    :rtype: str
    """
    return obj.__class__.__name__.lower()


def merge_dicts(a, b):
    """Merge b into a recursively, without overwriting values.

    :param dict a: the dict that will be altered with values of `b`.
    :rtype: None
    """
    for k, v in b.items():
        if isinstance(v, dict):
            merge_dicts(a.setdefault(k, {}), v)
        else:
            a.setdefault(k, v)


def random_bytes_hex(bytes_length):
    """Return a hexstring of bytes_length cryptographic-friendly random bytes.

    :param integer bytes_length: number of random bytes.
    :rtype: str
    """
    return hexlify(os.urandom(bytes_length)).decode('utf-8')


def native_value(value):
    """Convert string value to native python values.

    :param str value: value to interprete.
    :returns: the value coerced to python type
    """
    if isinstance(value, six.string_types):
        if value.lower() in ['on', 'true', 'yes']:
            value = True
        elif value.lower() in ['off', 'false', 'no']:
            value = False
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass
    return value


def read_env(key, value):
    """Read the setting key from environment variables.

    :param key: the setting name
    :param value: default value if undefined in environment
    :returns: the value from environment, coerced to python type
    """
    envkey = key.replace('.', '_').replace('-', '_').upper()
    return native_value(os.getenv(envkey, value))


def encode64(content):
    """Encode some content in base64.

    :rtype: str
    """
    return b64encode(content.encode('utf-8')).decode('utf-8')


def decode64(encoded_content):
    """Decode some base64 encoded content.

    :rtype: str
    """
    return b64decode(encoded_content.encode('utf-8')).decode('utf-8')


def Enum(**enums):
    return type('Enum', (), enums)


COMPARISON = Enum(
    LT='<',
    MIN='>=',
    MAX='<=',
    NOT='!=',
    EQ='==',
    GT='>',
)


def reapply_cors(request, response):
    """Reapply cors headers to the new response with regards to the request.

    We need to re-apply the CORS checks done by Cornice, in case we're
    recreating the response from scratch.

    """
    service = current_service(request)
    if service:
        request.info['cors_checked'] = False
        response = cors.ensure_origin(service, request, response)
    return response


def current_service(request):
    """Return the Cornice service matching the specified request.

    :returns: the service or None if unmatched.
    :rtype: cornice.Service
    """
    if request.matched_route:
        services = request.registry.cornice_services
        pattern = request.matched_route.pattern
        service = services[pattern]
        return service


def cached(ttl=None, prefix='cached_'):
    """Decorator to cache the result of a function or method into the
    configured cache backend.

    :param float ttl: expire after number of seconds.
    :param str prefix: prefix cache keys with specific string.

    .. code-block:: python

        EXPIRATION = 3600  # seconds.

        class Permissions(object):
            @cached(ttl=EXPIRATION)
            def has_perms(self, user_id):
                resp = requests.get('http://server/?allowed=' % user_id)
                return resp.status_code == 200

    """
    from pyramid.threadlocal import get_current_registry

    # On class method, skip ``self`` to compute cache key.
    frames = inspect.stack()
    defined_in_class = (len(frames) > 2 and
                        frames[2][4][0].strip().startswith('class '))
    skip_args = 1 if defined_in_class else 0

    # Get cache from current thread.
    cache = get_current_registry().cache

    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = prefix + func.__name__ + str(args[skip_args:]) + str(kwargs)
            cached = cache.get(key)
            if cached is None:
                cached = func(*args, **kwargs)
                cache.set(key, cached, ttl)
            return cached
        return wrapped

    return decorator
