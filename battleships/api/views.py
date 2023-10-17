from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, InviteSerializer, \
    InviteSendSerializer, GameSerializer, GameViewSerializer, BoardSerializer
from ..models import Game, Board, Invite
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from django.contrib.auth import get_user_model, login, logout
from .validators import register_validator, invite_validator, move_validator, setup_validator

UserModel = get_user_model()


class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        clean_data = register_validator(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.check_user(request.data)
        login(request, user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def list(self, request):
        queryset = UserModel.objects.exclude(id=request.user.id)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitesReceivedList(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def list(self, request):
        queryset = Invite.objects.filter(receiver__id=request.user.id)
        serializer = InviteSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitesSentList(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def list(self, request):
        queryset = Invite.objects.filter(sender__id=request.user.id)
        serializer = InviteSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InviteSend(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        cleaned_data = invite_validator(request.data, request.user.id)
        serializer = InviteSendSerializer(data=cleaned_data, context={'sender_id': request.user.id})
        if serializer.is_valid(raise_exception=True):
            invite = serializer.create(request.data)
            if invite:
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class InviteDecision(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    # accept invite and create game
    def put(self, request, pk):
        invite = Invite.objects.filter(id=pk)
        if invite:
            invite = invite[0]
            if invite.receiver.id == request.user.id:
                second_user = Invite.objects.filter(id=pk)[0].sender
                board = Board.objects.create(player_id=request.user.id, array=[[0] * 10] * 10)
                enemy_board = Board.objects.create(player_id=second_user.id, array=[[0] * 10] * 10)
                Game.objects.create(first_player_board_id=enemy_board.id, second_player_board_id=board.id)
                invite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # decline invite
    def delete(self, request, pk):
        invite = Invite.objects.filter(id=pk)
        if invite:
            invite = invite[0]
            if invite.receiver.id == request.user.id:
                invite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GamesList(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def list(self, request):
        queryset = Game.objects.filter(Q(first_player_board__player__id=request.user.id) |
                                       Q(second_player_board__player__id=request.user.id))
        dict_list = []
        for game in queryset:
            if game.second_player_board.player.id == request.user.id:
                enemy = game.first_player_board.player
                if game.current_player == 2:
                    players_turn = True
                else:
                    players_turn = False
            else:
                enemy = game.second_player_board.player
                if game.current_player == 1:
                    players_turn = True
                else:
                    players_turn = False

            dict_list.append({
                'id': game.id,
                'enemy': enemy,
                'result': game.result,
                'players_turn': players_turn
            })

        serializer = GameSerializer(dict_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GameView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request, pk):
        game = Game.objects.filter(id=pk)
        if game:
            game = game[0]
            if (
                game.first_player_board.player.id == request.user.id or
                game.second_player_board.player.id == request.user.id
            ):
                if game.first_player_board.player.id == request.user.id:
                    board = game.first_player_board
                    enemy_board = game.second_player_board
                    if game.current_player == 1:
                        players_turn = True
                    else:
                        players_turn = False
                else:
                    board = game.second_player_board
                    enemy_board = game.first_player_board
                    if game.current_player == 2:
                        players_turn = True
                    else:
                        players_turn = False

                # remove all boats form enemy board
                for i in range(10):
                    for j in range(10):
                        if enemy_board.array[i][j] > 0:
                            enemy_board.array[i][j] = 0

                serializer = GameViewSerializer({
                    'enemy_board': enemy_board,
                    'player_board': board,
                    'players_turn': players_turn})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # preparation phase
    def post(self, request, pk):
        game = Game.objects.filter(id=pk)
        if game:
            game = game[0]
            if (
                (game.first_player_board.player.id == request.user.id or
                 game.second_player_board.player.id == request.user.id) and
                game.result == 0
            ):
                if game.first_player_board.player.id == request.user.id:
                    board = game.first_player_board
                else:
                    board = game.second_player_board

                if board.preparation_phase:
                    arr = setup_validator(request.data)
                    board.preparation_phase = False
                    board.array = arr
                    serializer = BoardSerializer(board)
                    board.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # move
    def put(self, request, pk):
        game = Game.objects.filter(id=pk)
        if game:
            game = game[0]
            if (
                (game.first_player_board.player.id == request.user.id or
                 game.second_player_board.player.id == request.user.id) and
                game.result == 0
            ):
                if game.first_player_board.player.id == request.user.id:
                    if game.current_player == 2:
                        return Response('Not Your turn!', status=status.HTTP_400_BAD_REQUEST)
                    enemy_board = game.second_player_board
                    board = game.first_player_board
                else:
                    if game.current_player == 1:
                        return Response('Not Your turn!', status=status.HTTP_400_BAD_REQUEST)
                    enemy_board = game.first_player_board
                    board = game.second_player_board

                cleaned_data = move_validator(request.data, enemy_board, board)
                x = int(cleaned_data['x'])
                y = int(cleaned_data['y'])
                if enemy_board.array[y][x] == 0:
                    enemy_board.array[y][x] = -1
                    result = 'Missed'
                elif enemy_board.array[y][x] > 0:
                    enemy_board.array[y][x] = -2
                    enemy_board.ships_element_left -= 1

                    if enemy_board.ships_element_left == 0:
                        if game.first_player_board.player.id == request.user.id:
                            game.result = 1
                        else:
                            game.result = 2
                        result = 'You Won!'
                    else:
                        result = 'Hit!'

                enemy_board.save()

                if game.current_player == 1:
                    game.current_player = 2
                else:
                    game.current_player = 1

                game.save()
                return Response({'result': result}, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
