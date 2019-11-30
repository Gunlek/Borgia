from users.models import User
from shops.models import Product, Shop
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name', 'email', 'surname', 'family', 'balance', 'year', 'campus', 'phone']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit', 'is_manual', 'manual_price', 'correcting_factor', 'is_active', 'is_removed', 'shop_id']