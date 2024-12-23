from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from utils.NotFoundExtended import NotFoundExtended

# from rest_framework.pagination import PageNumberPagination
# from rest_framework.response import Response
# from rest_framework.exceptions import NotFound
# from collections import OrderedDict

class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count if hasattr(self, 'page') else len(data)),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link() if hasattr(self, 'page') else None),
            ('previous', self.get_previous_link() if hasattr(self, 'page') else None),
            ('results', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size == 0:
                    return None  # Return None to indicate no pagination
                if page_size > self.max_page_size:
                    return self.max_page_size
                return page_size
            except (KeyError, ValueError):
                pass
        return self.page_size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self.request = request  # Set the request attribute here
        page_size = self.get_page_size(request)
        
        # If page_size is None (from get_page_size returning None), return all data
        if page_size is None:
            return list(queryset)

        if not page_size:
            return None

        queryset = queryset
        
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            output_data = {
                "error": {"code": 104, "error_details": 'Invalid page.'},
                "pagination": {
                    "count": None,
                    "page_size": None,
                    "next": None,
                    "previous": None
                },
                "data": None,
                "status": False,
                "status_code": 104,
                "msg": 'Failed',
            }
            raise NotFound(output_data)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        self.page_size = page_size  # Ensure page_size is set on the instance
        return list(self.page)
    
class CustomLimitPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100



class NoLimitPagination(LimitOffsetPagination): 
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request
        self.display_page_controls = False
        

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2
