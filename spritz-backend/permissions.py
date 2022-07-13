from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode
from django.conf import settings
from django.http import HttpRequest
from rest_framework.permissions import BasePermission


class VKAccessPermission(BasePermission):
    def has_permission(self, request: HttpRequest, view):
        headers = request.META
        return self._is_valid(headers)

    @staticmethod
    def _is_valid(query: dict) -> bool:
        """Check VK Apps signature"""
        vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
        hash_code = b64encode(HMAC(settings.VK_SECRET.encode(),
                                   urlencode(vk_subset, doseq=True).encode(), sha256).digest())
        decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
        return query["sign"] == decoded_hash_code
