from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """Pagination for Course views."""

    page_size = 5  # Количество курсов на странице
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 50  # Максимальное количество на странице


class LessonPagination(PageNumberPagination):
    """Pagination for Lesson views."""

    page_size = 10  # Количество уроков на странице
    page_size_query_param = "page_size"
    max_page_size = 100
