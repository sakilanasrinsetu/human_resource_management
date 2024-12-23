from rest_framework.exceptions import NotFound,ErrorDetail, APIException
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class NotFoundExtended(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = str(self.default_detail)
        if code is None:
            code = str(self.default_code)

        self.detail = detail