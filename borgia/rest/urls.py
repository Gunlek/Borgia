from django.urls import include, path
from rest import views

rest_patterns = [
    path('api/', include([
        path('users', views.UserViewSet.as_view({'get': 'list'}), name='rest_user_list')
    ])),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework'))
]
