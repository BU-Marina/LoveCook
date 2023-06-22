from rest_framework.pagination import CursorPagination, PageNumberPagination


class CursorSetPagination(CursorPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    # ordering = '-created'


class LimitPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100

