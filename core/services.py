from pathlib import Path
from django.contrib.auth.models import User
from .models import Rodada, Partida, Classificacao, OrcamentoTime, DadosEafc
from django.db.models import Q
from django.db import IntegrityError
from .api_times import get_api_eafc
from collections import defaultdict

import datetime
import notifypy
import pandas as pd
import os
import locale


BASE_DIR = Path(__file__).resolve().parent.parent

def gerar_confrontos():
    usuarios = list(User.objects.all())
    confrontos = []

    for i in range(len(usuarios)):
        for j in range(i + 1, len(usuarios)):
            time_casa = usuarios[i]
            time_visitante = usuarios[j]
            confrontos.append((time_casa, time_visitante))

    return confrontos


def criar_jogos():
    # Verificar se já existem jogos no banco de dados
    if Partida.objects.exists():
        print("Jogos já criados.")
        return

    confrontos = gerar_confrontos()
    data_inicial = datetime.date(2024, 8, 1)  # Data inicial dos jogos
    dias_intervalo = 7  # Intervalo de uma semana entre os jogos
    print(confrontos)
    for i, (time_casa, time_visitante) in enumerate(confrontos):
        data_jogo = data_inicial + datetime.timedelta(days=i * dias_intervalo)
        Partida.objects.create(time_casa=time_casa, time_visitante=time_visitante)

        # Criando jogo de volta
        data_jogo_volta = data_jogo + datetime.timedelta(days=dias_intervalo * len(confrontos))
        Partida.objects.create(time_casa=time_visitante, time_visitante=time_casa)

def atualizar_classificacao(jogo):
    casa = getattr(jogo, 'time_casa')
    visitante = getattr(jogo, 'time_visitante')
    placar_casa = getattr(jogo, 'placar_casa')
    placar_visitante = getattr(jogo, 'placar_visitante')

    time_casa = Classificacao.objects.get(usuario=casa)
    time_visitante = Classificacao.objects.get(usuario=visitante)

    orcamento_casa = OrcamentoTime.objects.get(usuario=casa)
    orcamento_visitante = OrcamentoTime.objects.get(usuario=visitante)

    if placar_casa > placar_visitante:
        time_casa.pontos += 3
        time_casa.vitoria += 1
        time_visitante.derrota += 1
        orcamento_casa.dinheiro_time += 4000
        orcamento_visitante.dinheiro_time += 2000

    elif placar_casa < placar_visitante:
        time_visitante.pontos += 3
        time_visitante.vitoria += 1
        time_casa.derrota += 1
        orcamento_visitante.dinheiro_time += 4000
        orcamento_casa.dinheiro_time += 2000

    else:
        time_casa.pontos += 1
        time_visitante.pontos += 1
        time_casa.empate += 1
        time_visitante.empate += 1
        orcamento_casa.dinheiro_time += 4000
        orcamento_visitante.dinheiro_time += 2000

    time_casa.jogos += 1
    time_casa.gols_pro += placar_casa
    time_casa.gols_contra += placar_visitante
    time_casa.saldo_gols = (time_casa.gols_pro - time_casa.gols_contra)

    time_visitante.jogos += 1
    time_visitante.gols_pro += placar_visitante
    time_visitante.gols_contra += placar_casa
    time_visitante.saldo_gols = (time_visitante.gols_pro - time_visitante.gols_contra)

    time_casa.save()
    time_visitante.save()
    orcamento_casa.save()
    orcamento_visitante.save()


def reset_jogador():
    jogadores = DadosEafc.objects.filter(time_usuario__isnull=False)
    if jogadores:
        for jogador in jogadores:
            jogador.preco = 2000
            jogador.salario = 200
            jogador.time_usuario = None
            jogador.save()
        print("Jogadores dos clubes resetado")
    else:
        jogadores = DadosEafc.objects.all()
        for jogador in jogadores:
            jogador.preco = 2000
            jogador.salario = 200
            jogador.time_usuario = None
            jogador.save()
        print("Jogadores sem clubes resetado")


def reset_orcamento():
    usuarios = OrcamentoTime.objects.all()
    for usuario in usuarios:
        usuario.dinheiro_time = 30000
        usuario.salario_time = 0
        usuario.saldo = 30000
        usuario.save()


def notificacao(titulo, mensagem):
	notificar = notifypy.Notify(enable_logging=True)
	notificar.application_name = "Notificação"
	notificar.title = titulo
	notificar.message = mensagem
	notificar.urgency = "normal"
	notificar.icon = "static/assets/img/favicon.png"


	notificar.send(block=False)

def truncate_string(value, max_length):
    return value[:max_length] if isinstance(value, str) else value

def dados_fifa():
    nomes = []
    overall = []
    posicoes = []
    imagens = []
    dataFrame = pd.read_excel(os.path.join(BASE_DIR, 'arquivos/jogadores_novos.xlsx'))
    # print(dataFrame)
    for index, row in dataFrame.iterrows():

        jogadores  = DadosEafc.objects.create(
            nome=truncate_string(row['Nomes'], 200),
            overall=truncate_string(row['Overall'], 200),
            posicao=truncate_string(row['Posicao'], 200),
            avatar=truncate_string(row['Imagem'], 200),
            )
        jogadores.save()



def resetar_campeonato():
    usuarios = Classificacao.objects.all()
    for usuario in usuarios:
        usuario.pontos = 0
        usuario.vitoria = 0
        usuario.empate = 0
        usuario.derrota = 0
        usuario.gols_pro = 0
        usuario.gols_contra = 0
        usuario.saldo_gols = 0
        usuario.save()


def moeda(dinheiro):
    valor = dinheiro
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor = locale.currency(valor, grouping=True, symbol=None)
    return valor

def contagens_gols_assistencia(dados):
    contagens = defaultdict(int)

    for jogador in dados:
        contagens[jogador] += 1

    return contagens
