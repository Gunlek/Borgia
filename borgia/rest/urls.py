from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns
from rest import views

rest_patterns = [
    path('api/', include([
        path('users/', views.UserList.as_view()),
        path('users/<int:pk>/', views.UserDetail.as_view())
    ])),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework'))
]

rest_patterns = format_suffix_patterns(rest_patterns)
