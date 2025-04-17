from collections import OrderedDict
from rest_framework.pagination import LimitOffsetPagination as BaseLimitOffsetPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


class LimitOffsetPagination(BaseLimitOffsetPagination):
    default_limit = 20
    max_limit = 1000

    def get_limit(self, request):
        raw_value = request.query_params.get(self.limit_query_param)

        if raw_value in (None, "", "null", "None"):
            return self.default_limit

        try:
            return self._positive_int(raw_value, strict=True, cutoff=self.max_limit)
        except (TypeError, ValueError):
            raise NotFound(detail=f"Invalid limit value: {raw_value!r}")

    def get_paginated_response(self, data, extra_context=None):
        extra_context = extra_context or {}
        return Response(
            OrderedDict(
                {
                    "total": self.count,
                    "count": len(data),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                    **extra_context,
                }
            )
        )
