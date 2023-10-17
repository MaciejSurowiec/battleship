from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from battleships.models import Game, Board

UserModel = get_user_model()
BASE_URL = '/battleships/api'
EMPTY_BOARD = [[0] * 10] * 10


class GameApiTest(APITestCase):
    def test_game_view(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board2 = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board3 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board4 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board5 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board1.array = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [5, -2, 5, 5, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        board1.save()

        game = Game.objects.create(first_player_board_id=board1.id,
                                   second_player_board_id=board.id)
        Game.objects.create(first_player_board_id=board2.id, second_player_board_id=board3.id)
        Game.objects.create(first_player_board_id=board4.id, second_player_board_id=board5.id)

        self.client.login(username='testUser', password='qwertyui')
        result = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        response = self.client.get(BASE_URL + '/games/' + str(game.id))
        data = {'enemy_board':  {'array': result, 'preparation_phase': True, 'player': user1.id},
                'player_board': {'array': EMPTY_BOARD, 'preparation_phase': True, 'player': user.id},
                'players_turn': False}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

    def test_game_view_non_existing_game(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        game = Game.objects.create(first_player_board_id=board1.id,
                                   second_player_board_id=board.id)

        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/games/' + str(game.id + 1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_game_view_different_user_game(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board2 = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board3 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board4 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board5 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        Game.objects.create(first_player_board_id=board1.id,
                            second_player_board_id=board.id)
        Game.objects.create(first_player_board_id=board2.id, second_player_board_id=board3.id)
        game = Game.objects.create(first_player_board_id=board4.id, second_player_board_id=board5.id)
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/games/' + str(game.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_list(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board2 = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board3 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board4 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board5 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        g = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        g1 = Game.objects.create(first_player_board_id=board2.id, second_player_board_id=board3.id)
        Game.objects.create(first_player_board_id=board4.id, second_player_board_id=board5.id)

        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/games')
        data = [{'id': g.id, 'enemy': {'username': user1.username, 'id': user1.id}, 'result': 0, 'players_turn': False},
                {'id': g1.id, 'enemy': {'username': user2.username, 'id': user2.id}, 'result': 0, 'players_turn': True}]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

    def test_game_list_empty_list(self):
        UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        user2 = UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board4 = Board.objects.create(player_id=user2.id, array=EMPTY_BOARD)
        board5 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        Game.objects.create(first_player_board_id=board4.id, second_player_board_id=board5.id)

        self.client.login(username='testUser', password='qwertyui')
        response = self.client.get(BASE_URL + '/games')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_game_list_no_logged_user(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)

        response = self.client.get(BASE_URL + '/games')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_move_miss(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        game.current_player = 2
        game.save()
        self.client.login(username='testUser', password='qwertyui')

        data = {'x': 1, 'y': 4}
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 'Missed')
        board1 = Board.objects.filter(id=board1.id)[0]
        result = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(board1.array, result)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 1)

    def test_game_move_hit(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.preparation_phase = False
        board1.array = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [5, 5, 5, 5, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id, current_player=2)

        self.client.login(username='testUser', password='qwertyui')

        data = {'x': 1, 'y': 4}
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 'Hit!')
        board1 = Board.objects.filter(id=board1.id)[0]
        result = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [5, -2, 5, 5, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(board1.array, result)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 1)

    def test_game_move_no_logged_user(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        game.current_player = 2
        game.save()
        data = {'x': 1, 'y': 4}
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(board1.array, EMPTY_BOARD)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_move_different_user_game(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        game.current_player = 2
        game.save()
        data = {'x': 1, 'y': 4}
        self.client.login(username='testUser2', password='qwertyui')
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)

        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(board1.array, EMPTY_BOARD)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_move_out_of_range(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        game.current_player = 2
        game.save()
        data = {'x': 1, 'y': 11}
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)

        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board1.array, EMPTY_BOARD)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_move_already_bombed(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board1.array = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id, current_player=2)
        game.save()
        result = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        data = {'x': 1, 'y': 4}
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        game = Game.objects.filter(id=game.id)[0]
        board1 = Board.objects.filter(id=board1.id)[0]
        board = Board.objects.filter(id=board.id)[0]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board1.array, result)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_move_game_ended(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD, preparation_phase=False)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD, preparation_phase=False)

        game = Game.objects.create(first_player_board_id=board1.id,
                                   second_player_board_id=board.id,
                                   current_player=2,
                                   result=1)

        data = {'x': 1, 'y': 4}
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(game.result, 1)

    def test_game_move_last_move(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD, ships_element_left=1)
        board.preparation_phase = False
        board1.array = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        board1.preparation_phase = False
        board.save()
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id, current_player=2)
        game.save()
        result = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, -2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        data = {'x': 1, 'y': 4}
        self.client.login(username='testUser', password='qwertyui')
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        game = Game.objects.filter(id=game.id)[0]
        board1 = Board.objects.filter(id=board1.id)[0]
        board = Board.objects.filter(id=board.id)[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'result': 'You Won!'})
        self.assertEqual(board1.array, result)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 1)
        self.assertEqual(game.result, 2)

    def test_game_move_before_players_setup(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board1.preparation_phase = False
        board1.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id, current_player=2)
        self.client.login(username='testUser', password='qwertyui')

        data = {'x': 1, 'y': 4}
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(board1.array, EMPTY_BOARD)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_move_before_enemy_setup(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id, current_player=2)
        self.client.login(username='testUser', password='qwertyui')

        data = {'x': 1, 'y': 4}
        response = self.client.put(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        game = Game.objects.filter(id=game.id)[0]
        self.assertEqual(board1.array, EMPTY_BOARD)
        self.assertEqual(board.array, EMPTY_BOARD)
        self.assertEqual(game.current_player, 2)

    def test_game_setup(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser', password='qwertyui')
        data = {'array': [
            [5, 5, 5, 5, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        board = Board.objects.filter(id=board.id)[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(board.array, data['array'])

    def test_game_setup_no_logged_user(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        data = {'array': [
            [5, 5, 5, 5, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(board.array, EMPTY_BOARD)

    def test_game_setup_different_user_game(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)

        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser2', password='qwertyui')

        data = {'array': [
            [5, 5, 5, 5, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(board.array, EMPTY_BOARD)

    def test_game_setup_wrong_arrangement(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser', password='qwertyui')
        data = {'array': [
            [5, 5, 5, 0, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board.array, EMPTY_BOARD)
        data = {'array': [
            [5, 5, 5, 5, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 5, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board.array, EMPTY_BOARD)

    def test_game_setup_wrong_size(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser', password='qwertyui')
        data = {'array': [
            [5, 5, 5, 0, 5, 3, 3, 3, 2, 2, 0],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2, 0],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board.array, EMPTY_BOARD)

    def test_game_setup_game_already_setup(self):
        user = UserModel.objects.create_user(username='testUser', password='qwertyui')
        user1 = UserModel.objects.create_user(username='testUser1', password='qwertyui')
        UserModel.objects.create_user(username='testUser2', password='qwertyui')

        board = Board.objects.create(player_id=user.id, array=EMPTY_BOARD)
        board1 = Board.objects.create(player_id=user1.id, array=EMPTY_BOARD)
        board.preparation_phase = False
        board.save()
        game = Game.objects.create(first_player_board_id=board1.id, second_player_board_id=board.id)
        self.client.login(username='testUser', password='qwertyui')

        data = {'array': [
            [5, 5, 5, 5, 5, 3, 3, 3, 2, 2],
            [4, 4, 4, 4, 4, 4, 4, 4, 2, 2],
            [3, 3, 3, 3, 3, 3, 2, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]}
        response = self.client.post(BASE_URL + '/games/' + str(game.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(board.array, EMPTY_BOARD)
