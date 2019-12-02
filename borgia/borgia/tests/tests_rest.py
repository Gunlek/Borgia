from rest_framework.reverse import reverse
from django.test import TestCase, Client
from rest_framework.test import APIRequestFactory, force_authenticate
from rest.views import UserDetail, UserList
from users.models import User


class UserAuthFreeRESTApiTest(TestCase):
    url_api_list = 'api-list-users'
    url_api_detail = 'api-detail-user'

    def tests_get(self):
        response_list = Client().get(reverse(self.url_api_list))
        self.assertEqual(response_list.status_code, 200)

        response_detail = Client().get(reverse(self.url_api_detail, kwargs={'pk': 1}))
        self.assertEqual(response_detail.status_code, 403)

    def tests_alternative_get(self):
        response_list = Client().get("/api/users/")
        self.assertEqual(response_list.status_code, 200)

        response_detail = Client().get("/api/users/1/")
        self.assertEqual(response_detail.status_code, 403)

    def tests_post(self):
        response_list = Client().post(
            reverse(self.url_api_list),
            {'username': 'test_user'})

        self.assertEqual(response_list.status_code, 403)

    def tests_details(self):
        factory = APIRequestFactory()
        detail_view = UserDetail.as_view()
        request_update = factory.put(reverse(self.url_api_detail, kwargs={'pk': 1}), data={'balance': 58.0})
        response_update = detail_view(request_update)
        self.assertEqual(response_update.status_code, 403)

        request_delete = factory.put(reverse(self.url_api_detail, kwargs={'pk': 1}))
        response_delete = detail_view(request_delete)
        self.assertEqual(response_delete.status_code, 403)


class BaseUserAuthRESTApiTest(TestCase):
    fixtures = ['initial', 'tests_data']

    def setUp(self):
        self.user = User.objects.create(username='user')
        self.user.set_password('yaquela218quipine')
        self.user.save()


class UserAuthRESTApiTest(BaseUserAuthRESTApiTest):
    url_api_list = 'api-list-users'
    url_api_detail = 'api-detail-user'
    factory = APIRequestFactory()

    def setUp(self):
        super().setUp()

    def tests_get(self):
        factory = APIRequestFactory()
        list_view = UserList.as_view()
        request_create = factory.post(reverse(self.url_api_list), {'username': 'testUser'})
        force_authenticate(request_create, self.user)
        response_create = list_view(request_create)
        self.assertEqual(response_create.status_code, 201)

        factory = APIRequestFactory()
        detail_view = UserDetail.as_view()
        request_detail = factory.get(reverse(self.url_api_detail, kwargs={'pk': 1}))
        force_authenticate(request_detail, self.user)
        response_detail = detail_view(request_detail, pk=1)
        self.assertEqual(response_detail.status_code, 200)

    def tests_details(self):
        factory = APIRequestFactory()
        detail_view = UserDetail.as_view()
        request_update = factory.put(reverse(self.url_api_detail, kwargs={'pk': 1}), data={
            'balance': 58.0,
            'username': 'test'
        })
        force_authenticate(request_update, self.user)
        response_update = detail_view(request_update, pk=1)
        self.assertEqual(response_update.status_code, 200)

        request_delete = factory.delete(reverse(self.url_api_detail, kwargs={'pk': 1}))
        force_authenticate(request_delete, self.user)
        response_delete = detail_view(request_delete, pk=1)
        self.assertEqual(response_delete.status_code, 204)


