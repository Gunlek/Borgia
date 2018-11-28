import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from users.models import User
from django.contrib.auth.models import Group


# class GroupNode(DjangoObjectType):
#     class Meta:
#         model = Group
#         interfaces = (relay.Node, )
#         filter_fields = ['name']
#
# class UserNode(DjangoObjectType):
#     class Meta:
#         model = User
#         filter_fields = ['username', 'email', 'first_name', 'last_name']
#         interfaces = (relay.Node, )
#
#
# class Query(object):
#     user = relay.Node.Field(UserNode)
#     group = relay.Node.Field(GroupNode)
#
#     allUsers = DjangoFilterConnectionField(UserNode)
#     allGroups = DjangoFilterConnectionField(GroupNode)

class GroupType(DjangoObjectType):
    class Meta:
        model = Group


class UserType(DjangoObjectType):
    class Meta:
        model = User


class Query(object):
    # Groups
    all_groups = graphene.List(GroupType)

    def resolve_all_groups(self, info, **kwargs):
        return Group.objects.all()

    # Users
    user = graphene.Field(UserType,
                          id=graphene.Int(),
                          username=graphene.String())

    all_users = graphene.List(UserType)

    def resolve_all_users(self, info, **kwargs):
        # We can easily optimize query count in the resolve method
        return User.objects.all()

    def resolve_user(self, info, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
            return User.objects.get(pk=id)

        if username is not None:
            return User.objects.get(username=username)

        return None

