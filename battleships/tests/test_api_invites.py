from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from battleships.models import Invite, Game, Board

UserModel = get_user_model()
BASE_URL = '/battleships/api'


class InviteApiTest(APITestCase):
    def test_invite_received_list(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        invite1 = Invite.objects.create(sender_id=user2.id, receiver_id=user.id)
        Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/invites/received')
        data = [{'id': invite.id, 'sender': user1.id, 'receiver': user.id},
                {'id': invite1.id, 'sender': user2.id, 'receiver': user.id}]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

    def test_invite_received_list_no_logged_user(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        Invite.objects.create(sender_id=user2.id, receiver_id=user.id)
        Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        response = self.client.get(BASE_URL + '/invites/received')
        data = [{'sender': user1.id, 'receiver': user.id}, {'sender': user2.id, 'receiver': user.id}]
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEquals(response.data, data)

    def test_invite_sent_list(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        invite = Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        invite1 = Invite.objects.create(sender_id=user.id, receiver_id=user2.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/invites/sent')
        data = [{'id': invite.id, 'sender': user.id, 'receiver': user1.id},
                {'id': invite1.id, 'sender': user.id, 'receiver': user2.id}]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

    def test_invite_sent_list_no_logged_user(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')
        Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        Invite.objects.create(sender_id=user.id, receiver_id=user2.id)
        response = self.client.get(BASE_URL + '/invites/sent')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_send(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user1.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Invite.objects.all()), 1)

    def test_invite_send_when_invite_exist(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Invite.objects.all()), 1)

    def test_invite_send_when_game_exist(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        board = Board.objects.create(player_id=user.id, array=[[0] * 10] * 10)
        board1 = Board.objects.create(player_id=user1.id, array=[[0] * 10] * 10)
        Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Invite.objects.all()), 0)
        #self.client.logout()
        self.client.login(username='testUser1', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Invite.objects.all()), 0)

    def test_invite_send_no_logged_user(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Invite.objects.all()), 0)

    def test_invite_send_sender_equals_receiver(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.post(BASE_URL + '/invites/send', {'receiver': user.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Invite.objects.all()), 0)

    def test_invite_accept(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.put(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Game.objects.all()), 1)
        self.assertEqual(Game.objects.all()[0].first_player_board.player.id, user1.id)
        self.assertEqual(Game.objects.all()[0].second_player_board.player.id, user.id)

    def test_invite_accept_different_user_invite(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        self.client.login(username='testUser1', password='qwertyui')
        response = self.client.put(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Game.objects.all()), 0)
        self.client.login(username='testUser2', password='qwertyui')
        response = self.client.put(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Game.objects.all()), 0)

    def test_invite_accept_non_existing_invite(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        response = self.client.put(BASE_URL + '/invites/' + str(invite.id + 1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(Game.objects.all()), 0)
        self.assertEqual(len(Invite.objects.all()), 1)

    def test_invite_decline(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.delete(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Game.objects.all()), 0)
        self.assertEqual(len(Invite.objects.all()), 0)

    def test_invite_decline_different_user_invite(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')
        invite = Invite.objects.create(sender_id=user.id, receiver_id=user1.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.delete(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Game.objects.all()), 0)
        self.assertEqual(len(Invite.objects.all()), 1)
        self.client.login(username='testUser2', password='qwertyui')
        response = self.client.delete(BASE_URL + '/invites/' + str(invite.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(Game.objects.all()), 0)
        self.assertEqual(len(Invite.objects.all()), 1)

    def test_invite_decline_non_existing_invite(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        self.client.login(username='testUser', password='qwertyui')
        invite = Invite.objects.create(sender_id=user1.id, receiver_id=user.id)
        response = self.client.delete(BASE_URL + '/invites/' + str(invite.id + 1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(Game.objects.all()), 0)
        self.assertEqual(len(Invite.objects.all()), 1)
