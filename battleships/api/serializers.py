from django.core.exceptions import ValidationError

from ..models import Game, Board, Invite
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

    def create(self, validated_data):
        user_obj = UserModel.objects.create_user(password=validated_data["password"],
                                                 username=validated_data["username"])

        return user_obj


class UserLoginSerializer(serializers.Serializer):
    class Meta:
        username = serializers.CharField(max_length=255)
        password = serializers.CharField(
            style={'input_type': 'password'},
            trim_whitespace=False,
            max_length=128,
            write_only=True
        )

    def check_user(self, data):
        username = data['username']
        password = data['password']
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.',
                                                  code='authorization')
        else:
            raise serializers.ValidationError('Must include "username" and "password".',
                                              code='authorization')

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username']


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ['id', 'sender', 'receiver']


class InviteSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ['receiver']

    def create(self, validated_data):
        invite_obj = Invite.objects.create(sender_id=self.context.get('sender_id'),
                                           receiver_id=validated_data['receiver'])
        return invite_obj


class GameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    enemy = UserSerializer()
    result = serializers.IntegerField()
    players_turn = serializers.BooleanField()


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['array', 'preparation_phase', 'player']


class GameViewSerializer(serializers.Serializer):
    enemy_board = BoardSerializer()
    player_board = BoardSerializer()
    players_turn = serializers.BooleanField()
