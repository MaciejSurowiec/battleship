from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.sign_in, name='login'),
    path('register/', views.sign_up, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('invite/', views.send_invite, name='invite'),
    path('invite/<int:id>', views.process_invite, name='decline_invite'),
    path('game/<int:id>', views.game_view, name='game'),
    path('game/<int:id>/setup/', views.game_setup, name='game_setup'),
    path('game/<int:id>/move/', views.game_move, name='game_move'),
    path('api/', include('battleships.api.urls'))
]
