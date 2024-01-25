import logging
from functools import wraps

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class BaseGenericApiViewDecorator(object):
    def __init__(self, post=True, get=False, delete=False, put=False):
        self.get = get
        self.post = post
        self.delete = delete
        self.put = put

    def __call__(self, klass):
        if self.get:
            self.decorate_method(klass, "get")
        if self.post:
            self.decorate_method(klass, "post")
        if self.delete:
            self.decorate_method(klass, "delete")
        if self.put:
            self.decorate_method(klass, "put")
        return klass

    def decorate_method(self, klass, method):
        raise NotImplementedError("Please Implement this method")


class IsValidGenericApi(BaseGenericApiViewDecorator):
    def decorate_method(self, klass, method):
        old_method = getattr(klass, method)

        @wraps(getattr(klass, method))
        def decorated_method(self, request, **kwargs):
            data = request.data
            keyword_args = {**kwargs}
            if request.method == "GET":
                data = request.GET.copy()
            if keyword_args:
                data.update(**kwargs)
            context_kwargs = self.get_serializer_context()
            serializer = self.get_serializer_class()(data=data, context=context_kwargs)
            # serializer = self.get_serializer_class()(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                logger.warning(str(e))
                raise e
            return old_method(self, request, serializer)

        setattr(klass, method, decorated_method)
        return klass
