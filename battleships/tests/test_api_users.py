from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

UserModel = get_user_model()
BASE_URL = '/battleships/api'


class ApiUserTest(APITestCase):
    def test_register(self):
        response = self.client.post(BASE_URL + '/users/register', {'username': 'testUser', 'password': 'test1234'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(UserModel.objects.all()), 1)
        self.assertTrue(self.client.login(username='testUser', password='test1234'))

    def test_register_existing_user(self):
        UserModel.objects.create_user(username='testUser', password="12345678")
        response = self.client.post(BASE_URL + '/users/register', {'username': 'testUser', 'password': 'test1234'})
        self.assertEqual(len(UserModel.objects.all()), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/users/login', {'username': 'testUser', 'password': 'qwertyui'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/users/login', {'username': 'testUser', 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_non_existing_user(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/users/login', {'username': 'testuser', 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_info(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/users')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = [{'id': user1.id, 'username': user1.username}, {'id': user2.id, 'username': user2.username}]
        self.assertEqual(response.data, data)

    def test_user_info_no_logged_user(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        response = self.client.get(BASE_URL + '/users')
        data = [{'id': user1.id, 'username': user1.username}, {'id': user2.id, 'username': user2.username}]
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEquals(response.data, data)

    def test_user_logout(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        self.client.post(BASE_URL + '/users/logout')
        response = self.client.get(BASE_URL + '/users')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # checked if logged out worked, should be changed to something different
