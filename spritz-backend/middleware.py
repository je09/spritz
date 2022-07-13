from urllib.parse import urlparse, parse_qsl
from django.http import HttpRequest


class VKStartParamParserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest, *args, **kwargs):
        params = dict(parse_qsl(urlparse(request.META.get('HTTP_PARAMS')).query, keep_blank_values=True))
        for k, v in params.items(): request.META.setdefault(k, v)

        return self.get_response(request)
