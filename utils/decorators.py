from functools import wraps

from utils.actions import activity_log


def log_activity(func):
    @wraps(func)
    def wrapper(viewset, request, *args, **kwargs):
        # Check if the request method is GET
        if request.method == 'GET':
            return func(viewset, request, *args, **kwargs)
        
        # Proceed with logging activity for other request methods
        response = func(viewset, request, *args, **kwargs)
        try:
            if response.status_code in [200, 201]:
                instance = viewset.get_object() if 'retrieve' in func.__name__ else viewset.queryset.filter(**kwargs).last()
                serializer = viewset.get_serializer(instance)
                activity_log(instance, request, serializer)
            elif response.status_code in [400, 401, 404, 406, 405]:
                instance = viewset.get_object() if 'retrieve' in func.__name__ else viewset.queryset.filter(**kwargs).last()
                serializer = viewset.get_serializer(instance)
                activity_log(instance, request, serializer)
        except:
            pass
        
        return response

    return wrapper