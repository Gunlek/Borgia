from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns
from rest import views

rest_patterns = [
    path('api/', include([
        path('users/', views.UserList.as_view()),
        path('users/<int:pk>/', views.UserDetail.as_view()),
        path('products/', views.ProductList.as_view()),
        path('products/<int:pk>/', views.ProductDetail.as_view()),
        path('shops/', views.ShopList.as_view()),
        path('shops/<int:pk>/', views.ShopDetail.as_view()),
        path('saleproducts/', views.SaleProductList.as_view()),
        path('saleproducts/<int:pk>/', views.SaleProductDetail.as_view()),
        path('sales/', views.SaleList.as_view()),
        path('sales/<int:pk>/', views.SaleDetail.as_view())
    ])),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework'))
]

rest_patterns = format_suffix_patterns(rest_patterns)
