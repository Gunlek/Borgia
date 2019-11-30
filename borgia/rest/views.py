from users.models import User
from rest.serializers import UserSerializer
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

