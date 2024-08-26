from django.urls import path
from .views import *
from .htmx_views import *

urlpatterns = [
    path('', homepage, name='homepage'),
    path('classificacao', classificacao, name='classificacao'),
    path('salvar-jogos', salvar_jogos, name='salvar_jogos'),
    path('meu-time/', meu_time, name='meu_time'),

    path('leiloes/', leiloes, name='leiloes'),
    path('leiloes/<int:player_id>/comprar/', comprar_jogador, name='comprar_jogador'),

    path('contratar-jogador/', contratar_jogador, name='contratar_jogador'),
    path('contratar-jogador/<int:id_jogador>/', contratar_jogador_time, name='contratar_jogador_time'),

    #views do superuser para configurar a plataforma
    path('gerar_jogos/', gerar_jogos, name='gerar_jogos'),
    path('criar-jogadores/', criar_jogadores, name='criar_jogadores'),
    path('criar-emblemas-times/', criar_emblemas_times, name='criar_emblemas_times'),
    path('zerar-classificacao/', zerar_pontos_classificacao, name='zerar_pontos_classificacao'),

    #trade
    path('trade_list/', trade_list, name='trade_list'),
    path('trade/select_players/', select_players_for_trade, name='select_players_for_trade'),
    path('trade/propose/<int:proposer_player_id>/<int:receiver_player_id>/', propose_trade,name='propose_trade'),
    path('trade/confirm/<int:trade_id>/', confirm_trade_proposer, name='confirm_trade_proposer'),
    path('trade/respond/<int:trade_id>/', respond_trade, name='respond_trade'),

    #perfil
    path('perfil', perfil, name='perfil'),


    #Login
    path('login/', fazer_login, name='login'),
    path('logout', fazer_logout, name='logout'),
]


# urls do HTMX
htmx_urlpatterns = [
    #noticias & notificacao
    path('load-news/', load_news, name='load_news'),
    path('load-notificacao/', load_notificacao, name='load_notificacao'),
    path('notificacoes/', ver_notificacoes, name='notificacoes'),
    path('notificacoes/marcar_como_lida/<int:notificacao_id>/', marcar_como_lida, name='marcar_como_lida'),
]


urlpatterns += htmx_urlpatterns
