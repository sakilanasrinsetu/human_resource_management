from rest_framework import permissions, status, views, viewsets
from utils.decorators import log_activity
from utils.generates import unique_slug_generator
from utils.response_wrapper import ResponseWrapper

from django.db.models import Q
from utils.actions import send_action, activity_log
from utils.permissions import CheckCustomPermission


# .....***..... There is Checking lookup Field both for slug and pk or ID .....***.....

def object_get(object_qs , **kwargs):
    if kwargs.get("pk") or kwargs.get("id"):
        try:
            pk = kwargs["pk"]
        except:
            pk = kwargs["id"]

        if not pk.isdigit():
            instance = object_qs.filter(slug__iexact = str(pk)).last()
        else:
            instance = object_qs.filter(id = pk).last()
        
        return instance
        
    elif kwargs.get("slug"):
        slug = kwargs["slug"]

        if not slug.isdigit():
            instance = object_qs.filter(slug__iexact = slug).last()
        elif slug.isdigit():
            instance = object_qs.filter(slug__iexact = str(slug)).last()
        else:
            instance = object_qs.filter(pk = int(slug)).last()

        return instance
    
    else:
        return None
    
# .....***..... END There is Checking lookup Field both for slug and pk or ID .....***.....

class CustomViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk' or "slug"
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        try:
            class_model_name = self.queryset.model.__name__
            model_name  = ''.join(['_' + c.lower() if c.isupper() else c for c in class_model_name]).lstrip('_')

            list_permission = f"can_view_list_{model_name}"
            add_permission = f"can_add_{model_name}"
            update_permission = f"can_update_{model_name}"
            destroy_permission = f"can_destroy_{model_name}"
            retrieve_permission = f"can_retrieve_{model_name}"
                
            
            if self.action in ["list"]:
                # permission_classes = [
                #     (CheckCustomPermission(list_permission))
                # ]
                permission_classes = [permissions.IsAuthenticated]
                
            elif self.action in ["create"]:
                # permission_classes = [
                #     (CheckCustomPermission(add_permission))
                # ]
                permission_classes = [permissions.IsAuthenticated]
            elif self.action in ["update"]:
                # permission_classes = [
                #     (CheckCustomPermission(update_permission))
                # ]
                permission_classes = [permissions.IsAuthenticated]
            elif self.action in ["destroy"]:
                # permission_classes = [
                #     (CheckCustomPermission(destroy_permission))
                # ]
                permission_classes = [permissions.IsAuthenticated]
            elif self.action in ["retrieve"]:
                # permission_classes = [
                #     (CheckCustomPermission(retrieve_permission))
                # ]
                permission_classes = [permissions.IsAuthenticated]
            else:
                permission_classes = [permissions.AllowAny]
            return [permission() for permission in permission_classes]
        
        except:
            permission_classes = [permissions.AllowAny]
            return [permission() for permission in permission_classes]

    
    # ..........***.......... Get All Data ..........***..........
    @log_activity
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()

        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)

        paginated_data = self.get_paginated_response(serializer.data)
        
        return ResponseWrapper(data=paginated_data.data, msg="Success", status=200)

    # ..........***.......... Create ..........***..........
    @log_activity
    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        
        serializer = serializer_class(data=request.data, partial=True)
        name = ''
        
        if request.data.get('name'):
            name = request.data.get('name')
        elif request.data.get('title'):
            name = request.data.get('title')
        else:
            name = name
            
        try:
            qs = self.queryset.filter(name = request.data.get('name')) or self.queryset.filter(title = request.data.get('title'))
            
            if qs:
                return ResponseWrapper(error_msg="Name is Already Found", error_code=400)
        except:
            pass
            
        if serializer.is_valid():
            if name:
                slug = unique_slug_generator(name = name) 
                
            serializer.validated_data['created_by'] = request.user
            try:
                serializer.validated_data['slug'] = slug
            except:
                pass
            
            try:
                qs = serializer.save()
                if slug:
                    qs.slug = slug
                    qs.save()
                    
            except:
                qs = serializer.save()

            # activity_log(qs, request,serializer)

            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    # ..........***.......... Update ..........***..........
    
    @log_activity
    def update(self, request, **kwargs):
        slug = None
        if request.data.get("slug"):
            slug = request.data.pop("slug")

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        if serializer.is_valid():
            object_qs = self.queryset
            qs = object_get(object_qs, **kwargs)

            if not qs:
                return ResponseWrapper(error_code=406, error_msg='Not Found', 
                status=406)
            
            # ....NOTE...: Unique Slug Check :....START....

            if slug and kwargs.get("slug"):
                slug_check_qs = self.queryset.filter(slug = slug).exclude(slug = kwargs.get("slug"))
                if slug_check_qs:
                    return ResponseWrapper(error_code=406, error_msg='Slug is Already Exist', status=406)
                
            else:
                pk_check_qs = self.queryset.filter(pk = kwargs.get("pk")).exclude(pk = kwargs.get("pk"))
                if pk_check_qs:
                    return ResponseWrapper(error_code=406, error_msg='Slug is Already Exist', status=406)
            
            # ....NOTE...: Unique Slug Check :....END....

            qs = serializer.update(instance=qs, validated_data=serializer.validated_data)

            if slug:
                qs.slug = slug
                qs.save()

            try:
                if qs:
                    qs.updated_by_id = self.request.user.id
                    qs.save()
            except:
                qs = qs

            serializer = self.serializer_class(instance=qs)

            # Save Logger for Tracking 
            # activity_log(qs, request,serializer)

            return ResponseWrapper(data=serializer.data, status = 200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    # ..........***.......... Delete ..........***..........

    @log_activity
    def destroy(self, request, **kwargs):
        object_qs = self.queryset
        qs = object_get(object_qs, **kwargs)

        if qs:
            qs.delete()
            # activity_log(qs, request,serializer=None)
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="failed to delete", error_code=400)

    # ..........***.......... Get Single Data ..........***..........

    @log_activity
    def retrieve(self, request, *args, **kwargs):
        object_qs = self.queryset
        qs = object_get(object_qs, **kwargs)
        if not qs:
            print('fffff')
            return ResponseWrapper(error_msg="Information is Not found", error_code=400)
        
        serializer = self.get_serializer(qs)
    
        return ResponseWrapper(data = serializer.data, msg="Success", status = 200)
        
