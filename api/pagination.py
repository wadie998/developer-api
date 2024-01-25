from rest_framework.pagination import PageNumberPagination


class ModelPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 100
