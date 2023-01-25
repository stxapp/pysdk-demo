from stxsdk.exceptions import BaseCustomException


class MarketsNotFoundException(BaseCustomException):
    pass


class OrderCreationFailure(BaseCustomException):
    pass
