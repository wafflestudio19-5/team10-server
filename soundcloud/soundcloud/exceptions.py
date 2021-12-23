from rest_framework.exceptions import APIException
from rest_framework import status


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('Already existing name.')
    default_code = 'conflict'