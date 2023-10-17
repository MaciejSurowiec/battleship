from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from battleships.models import Invite, Game

UserModel = get_user_model()


def register_validator(data):
    username = data['username'].strip()
    password = data['password'].strip()

    if not username or UserModel.objects.filter(username=username).exists():
        raise ValidationError('Choose another username')

    if not password or len(password) < 8:
        raise ValidationError('Choose another password, min 8 characters')

    return data


def invite_validator(data, sender_id):
    receiver_id = data['receiver'].strip()

    if sender_id == int(receiver_id):
        raise ValidationError('You cannot invite yourself')

    if not sender_id or not receiver_id:
        raise ValidationError('Sender and receiver are needed')

    game = Game.objects.filter(Q(first_player_board__player__id=sender_id,
                                 second_player_board__player__id=receiver_id) |
                               Q(first_player_board__player__id=receiver_id,
                                 second_player_board__player__id=sender_id))

    if game:
        if game.filter(result=0).exists():
            raise ValidationError('Finish game with this player before starting new')

    if Invite.objects.filter(sender_id=sender_id, receiver_id=receiver_id).exists():
        raise ValidationError('Invite already exist')

    return data


def move_validator(data, enemy_board, board):
    x = int(data['x'])
    y = int(data['y'])

    if enemy_board.preparation_phase:
        raise ValidationError('Wait till enemy setup their board')

    if board.preparation_phase:
        raise ValidationError('Setup board before attacking')

    if x < 0 or x > 9 or y < 0 or y > 9:
        raise ValidationError('Out of range')

    if enemy_board.array[y][x] < 0:
        raise ValidationError('Already bombed')

    return data


def setup_validator(data):
    arr = data.getlist('array')
    output = []

    if len(arr) != 10:
        raise ValidationError('Array should be 10x10')

    for i, row in enumerate(arr):
        if len(row.strip('][').split(', ')) != 10:
            raise ValidationError('Array should be 10x10')
        l = []
        for j, e in enumerate(row.strip('][').split(', ')):
            l.append(int(e))

        output.append(l)

    if sum(x.count(5) for x in output) != 5:
        raise ValidationError('There should be one boat with length of 5')

    if sum(x.count(4) for x in output) != 8:
        raise ValidationError('There should be two boat with length of 4')

    if sum(x.count(3) for x in output) != 9:
        raise ValidationError('There should be three boat with length of 3')

    if sum(x.count(2) for x in output) != 8:
        raise ValidationError('There should be four boat with length of 2')

    # check if the boats elements are placed correctly

    return output
