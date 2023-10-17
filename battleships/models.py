from django.db import models

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Board(models.Model):
    array = ArrayField(
        ArrayField(
            models.IntegerField(default=0),
            size=10,
        ),
        size=10,
    )
    ships_element_left = models.IntegerField(default=30)
    preparation_phase = models.BooleanField(default=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE)


class Game(models.Model):
    first_player_board = models.ForeignKey(Board, related_name='first_player_board', on_delete=models.CASCADE)
    second_player_board = models.ForeignKey(Board, related_name='second_player_board', on_delete=models.CASCADE)
    current_player = models.IntegerField(default=1)
    result = models.IntegerField(default=0)


class Invite(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
