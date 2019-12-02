from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns
from rest import views

rest_patterns = [
    path('api/', include([
        path('users/', views.UserList.as_view(), name="api-list-users"),
        path('users/<int:pk>/', views.UserDetail.as_view(), name="api-detail-user"),
        path('products/', views.ProductList.as_view(), name="api-list-products"),
        path('products/<int:pk>/', views.ProductDetail.as_view(), name="api-detail-product"),
        path('shops/', views.ShopList.as_view(), name="api-list-shops"),
        path('shops/<int:pk>/', views.ShopDetail.as_view(), name="api-detail-shop"),
        path('saleproducts/', views.SaleProductList.as_view(), name="api-list-saleproducts"),
        path('saleproducts/<int:pk>/', views.SaleProductDetail.as_view(), name="api-detail-saleproduct"),
        path('sales/', views.SaleList.as_view(), name="api-list-salelists"),
        path('sales/<int:pk>/', views.SaleDetail.as_view(), name="api-detail-salelist"),
        path('transferts/', views.SaleList.as_view(), name="api-list-transferts"),
        path('transferts/<int:pk>/', views.SaleDetail.as_view(), name="api-detail-transfert"),
        path('exceptionnalmovements/', views.ExceptionnalMovementList.as_view(), name="api-list-exceptionnalmovements"),
        path('exceptionnalmovements/<int:pk>/', views.ExceptionnalMovementDetail.as_view(), name="api-detail-exceptionnalmovement")
    ])),
    path('api-auth/', include('rest_framework.urls', namespace='rest-framework'))
]

rest_patterns = format_suffix_patterns(rest_patterns)
