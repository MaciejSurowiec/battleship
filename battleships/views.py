from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
import json

from .forms import LoginForm
from .models import Invite, Game, Board


def index(request):
    if request.user.is_authenticated:
        url_parameter = request.GET.get("q")
        if url_parameter:
            users_list = get_user_model().objects.filter(username__icontains=url_parameter)[:5]
        else:
            users_list = get_user_model().objects.exclude(id=request.user.id)[:5]

        invites = Invite.objects.filter(sender__id=request.user.id) | Invite.objects.filter(receiver__id=request.user.id)
        ids = []
        for invite in invites:
            if invite.receiver.id != request.user.id:
                ids.append(invite.receiver.id)
            else:
                ids.append(invite.sender.id)

        games = (Game.objects.filter(first_player_board__player__id=request.user.id) |
                 Game.objects.filter(second_player_board__player__id=request.user.id))

        for game in games:
            if game.first_player_board.player.id != request.user.id:
                ids.append(game.first_player_board.player.id)
            else:
                ids.append(game.second_player_board.player.id)

        is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest"
        received = Invite.objects.filter(receiver__id=request.user.id)
        if is_ajax_request:
            html = render_to_string(
                template_name="search_users.html",
                context={"users_list": users_list}
            )

            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)

        return render(request, 'index.html',
                      {"users_list": users_list, "invites": ids, "received_invites": received, "games": games})
    else:
        return render(request, 'index.html')


def sign_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'users/login.html',{'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}')
                return redirect('/battleships')

        form.error = 'Invalid username or password'
        return render(request, 'users/login.html', {'form': form})


def sign_up(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'users/register.html', {'form': form})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/battleships')

        return render(request, 'users/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('/battleships')


@login_required
def send_invite(request):
    if request.method == 'POST':
        Invite.objects.create(sender_id=request.user.id, receiver_id=request.body.decode('UTF-8'))
        return HttpResponse('')

@login_required
def process_invite(request, id):
    if request.method == 'DELETE':
        Invite.objects.filter(id=id).delete()
        return HttpResponse('')
    elif request.method == 'POST':
        second_user = Invite.objects.filter(id=id)[0].sender
        board = Board.objects.create(player_id=request.user.id, array=[[0]*10]*10)
        enemy_board = Board.objects.create(player_id=second_user.id, array=[[0]*10]*10)
        #for now sender is always first player but this can be randomized
        game = Game.objects.create(first_player_board_id=enemy_board.id, second_player_board_id=board.id)
        Invite.objects.filter(id=id).delete()

        # redirect to game view?
        return HttpResponse('')


@login_required
def game_view(request, id):
    game = Game.objects.filter(id=id)[0]
    if (game.first_player_board.player.id != request.user.id and
            game.second_player_board.player.id != request.user.id):
        return redirect("/battleships/")

    if game.first_player_board.player.id != request.user.id:
        enemy_board = game.first_player_board
        board = game.second_player_board
    else:
        board = game.first_player_board
        enemy_board = game.second_player_board

    if game.current_player == 0:
        if game.first_player_board.player.id == request.user.id:
            turn = 1
        else:
            turn = 0
    else:
        if game.first_player_board.player.id == request.user.id:
            turn = 0
        else:
            turn = 1

    # remove all boats form enemy board
    for i in range(10):
        for j in range(10):
            if enemy_board.array[i][j] > 0:
                enemy_board.array[i][j] = 0

    return render(request, 'users/game.html', {"board": board, "enemy_board": enemy_board, "turn": turn})


@login_required
def game_setup(request, id):
    if request.method == 'POST':
        array = json.loads(request.POST["array"])
        game = Game.objects.filter(id=id)[0]
        if game.first_player_board.player.id != request.user.id:
            board = game.second_player_board
        else:
            board = game.first_player_board

        board.array = array
        board.preparation_phase = False
        board.save()

        return redirect('/battleships/game/' + str(id))


@login_required
def game_move(request, id):
    if request.method == 'POST':
        # check if is this players turn
        x = int(request.POST["x"])
        y = int(request.POST["y"])
        game = Game.objects.filter(id=id)[0]
        if game.first_player_board.player.id != request.user.id:
            enemy_board = game.first_player_board
        else:
            enemy_board = game.second_player_board

        if enemy_board.array[y][x] == 0:
            enemy_board.array[y][x] = -1
        else:
            if enemy_board.array[y][x] > 0:
                enemy_board.array[y][x] = -2
                enemy_board.ships_element_left -= 1

            if enemy_board.ships_element_left == 0:
                if game.first_player_board.player.id == request.user.id:
                    game.result = 1
                else:
                    game.result = -1

        if game.current_player == 0:
            game.current_player = 1
        else:
            game.current_player = 0

        game.save()
        enemy_board.save()

        return redirect('/battleships/game/' + str(id))
