from users.models import User
from shops.models import Product, Shop
from sales.models import Sale, SaleProduct
from finances.models import Transfert
from rest.serializers import UserSerializer, ProductSerializer, ShopSerializer, SaleSerializer, SaleProductSerializer, TransfertSerializer
from rest_framework import permissions
from rest_framework import generics


class UserList(generics.ListCreateAPIView):
    """
    List all users or create a new user
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProductList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ShopList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ShopDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class SaleProductList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = SaleProduct.objects.all()
    serializer_class = SaleProductSerializer


class SaleProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = SaleProduct.objects.all()
    serializer_class = SaleProductSerializer


class SaleList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class SaleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class TransfertList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Transfert.objects.all()
    serializer_class = TransfertSerializer


class TransfertDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Transfert.objects.all()
    serializer_class = TransfertSerializer
