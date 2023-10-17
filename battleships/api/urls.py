from django.urls import path

from battleships.api import views

urlpatterns = [
    path('users/register', views.UserRegister.as_view(), name='api_register'),
    path('users/login', views.UserLogin.as_view(), name='api_login'),
    path('users/logout', views.UserLogout.as_view(), name='api_logout'),
    path('users', views.UserView.as_view(), name='api_users'),
    path('invites/received', views.InvitesReceivedList.as_view(), name='api_received_invites'),
    path('invites/sent', views.InvitesSentList.as_view(), name='api_sent_invites'),
    path('invites/send', views.InviteSend.as_view(), name='api_send_invite'),
    path('invites/<int:pk>', views.InviteDecision.as_view(), name='api_invite_decline'),
    path('games', views.GamesList.as_view(), name='api_games_list'),
    path('games/<int:pk>', views.GameView.as_view(), name='api_game_view'),
]
