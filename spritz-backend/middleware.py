from urllib.parse import urlparse, parse_qsl
from django.http import HttpRequest, HttpResponseForbidden
from rest_framework import exceptions


class VKStartParamParserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest, *args, **kwargs):
        params = dict(parse_qsl(urlparse(request.META.get('HTTP_PARAMS')).query, keep_blank_values=True))
        for k, v in params.items(): request.META.setdefault(k, v)

        if not request.META.get('vk_user_id'):
            return HttpResponseForbidden(exceptions.PermissionDenied.default_detail)

        return self.get_response(request)
