import logging

from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)


class ZeroBasedPagination(PageNumberPagination):
    page_size = 20
    page_query_param = "page"
    page_size_query_param = "size"

    def validate_number(self, number):
        """Validate the given 0-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_("That page number is not an integer"))

        if number < 0:
            raise EmptyPage(_("That page number is less than 0"))

        last_page_number = self.page.paginator.num_pages - 1  # Zero-based index of the last page
        if number > last_page_number:
            raise EmptyPage(_("That page contains no results"))

        return number

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        # Convert 0-based page number to 1-based
        page_number += 1

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            logger.warning(str(exc))
            return None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param, 0)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        # Convert to integer
        return int(page_number)


def generate_pagination_links(request, paginator, page_number):
    """
    Generate pagination links and headers.
    """
    base_url = request.build_absolute_uri()

    links = []
    if paginator.num_pages > 1:
        if page_number > 0:
            links.append(f'<{base_url}?page={page_number - 1}>; rel="prev"')
        if page_number < paginator.num_pages - 1:
            links.append(f'<{base_url}?page={page_number + 1}>; rel="next"')

    links.append(f'<{base_url}?page=0>; rel="first"')
    links.append(f'<{base_url}?page={paginator.num_pages - 1}>; rel="last"')

    headers = {"Link": ", ".join(links), "x-total-count": paginator.count}

    return headers


def generate_pagination_data(page_obj):
    """
    Generate pagination data.
    """
    if not page_obj:
        return {"pageable": None}
    pageable = {
        "offset": page_obj.paginator.per_page * (page_obj.number - 1),
        "paged": True,
        "pageNumber": page_obj.number - 1,
        "pageSize": page_obj.paginator.per_page,
        "sort": {"empty": True, "sorted": False, "unsorted": True},
        "unpaged": False,
    }

    response_data = {
        "empty": page_obj.paginator.count == 0,
        "first": page_obj.number == 1,
        "last": page_obj.number == page_obj.paginator.num_pages,
        "number": page_obj.number - 1,
        "numberOfElements": len(page_obj.object_list),
        "size": page_obj.paginator.per_page,
        "totalElements": page_obj.paginator.count,
        "totalPages": page_obj.paginator.num_pages,
        "pageable": pageable,
    }

    return response_data
