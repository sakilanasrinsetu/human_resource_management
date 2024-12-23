from django.urls import path

from .views import *

urlpatterns =[
    path('register/',
         UserViewSet.as_view({'post': 'register'}, name='register')),
    path('login/',
         UserViewSet.as_view({'post': 'login'}, name='login')),
    path('user_details/',
         UserViewSet.as_view({'get': 'user_details'}, name='user_details')),
    path('user/',
         UserViewSet.as_view({'get': 'list'}, name='user')),
    path('user/<pk>/',
         UserViewSet.as_view({'delete': 'destroy',
                              "patch":"update", "get":"retrieve"},
                              name='user')),
]