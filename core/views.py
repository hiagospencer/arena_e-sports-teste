from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import date

import threading
import pandas as pd
import locale
import decimal

from core.forms import *
from .models import *
from .api_times import *
from .services import *

@login_required(login_url="login/")
def homepage(request):
    user = request.user
    verificado = False
    comentarios = NotificacaoJogo.objects.all().order_by("-data")[:15]
    usuario_criado, criado = Verificacao.objects.get_or_create(user=user)
    usuario_orcamento, criado = OrcamentoTime.objects.get_or_create(usuario=user)
    usuario_classificacao, criado = Classificacao.objects.get_or_create(usuario=user)
    team, created = Team.objects.get_or_create(usuario=user)
    jogadores = DadosEafc.objects.filter(time_usuario=team)
    usuario = Usuario(usuario=user)
    dados = Usuario.objects.filter(usuario=user)
    orcamento = OrcamentoTime.objects.filter(usuario=user)
    quantidade_jogadores = len(jogadores)
    if usuario_criado.is_verificado == False:
        #funcionalidade para não ficar salvando sempre que entrar na views
        if usuario:
            usuario.save()
            usuario_orcamento.save()
            usuario_classificacao.save()
            usuario_criado.is_verificado = True
            usuario_criado.save()

    for item in dados:
        if item.email:
            verificado = True
            context = {"dados":dados, "verificado":verificado, "orcamento":orcamento,"jogadores":jogadores, "quantidade_jogadores": len(jogadores),"comentarios":comentarios}
            return render(request, 'index.html',context)
        else:
            verificado = False
            context = {"dados":dados, "verificado":verificado, "orcamento":orcamento,"jogadores":jogadores, "quantidade_jogadores": len(jogadores),"comentarios":comentarios}
            return render(request, 'index.html',context)

    context = {"dados":dados, "verificado":verificado, "orcamento":orcamento,"jogadores":jogadores, "quantidade_jogadores": len(jogadores),"comentarios":comentarios}
    return render(request, 'index.html',context)


@login_required(login_url="login/")
def classificacao(request):
    posicao_usuario = Classificacao.objects.filter(pagamento=True).order_by('-pontos', '-saldo_gols', '-vitoria')
    ano = date.today().year
    return render(request, 'classificacao.html', {'classificacao': posicao_usuario, "ano":ano})

def gols_assistencia(request):
    artilheiros = DadosEafc.objects.filter(gols__gte=1).order_by('-gols')
    assistencias = DadosEafc.objects.filter(assistencias__gte=1).order_by('-assistencias')
    return render(request,'gols_assistencia.html',{"artilheiros":artilheiros, "assistencias":assistencias})

@user_passes_test(lambda u: u.is_superuser)
def gerar_jogos(request):

    # Essa views só é acessada pelo o superuser
    if Partida.objects.exists():
        return HttpResponse('Jogos já foram criados anteriormente.')

    # criar_jogadores_banco_dados()
    criar_jogos()
    return HttpResponse('Jogos criados com sucesso!')


@user_passes_test(lambda u: u.is_superuser)
def criar_jogadores(request):
    # Essa views só é acessada pelo o superuser
    if DadosEafc.objects.exists():
        return HttpResponse('jogadores já foram criados anteriormente.')

    thread = threading.Thread(target=dados_fifa)
    thread.start()
    return HttpResponse('Jogadores criados com sucesso!')


@user_passes_test(lambda u: u.is_superuser)
def criar_emblemas_times(request):
    # Essa views só é acessada pelo o superuser
    get_api_data()
    return HttpResponse('Emblemas criados com sucesso!')


@user_passes_test(lambda u: u.is_superuser)
def zerar_pontos_classificacao(request):
    # Essa views só é acessada pelo o superuser
    reset_jogador()
    reset_orcamento()
    resetar_campeonato()
    return render(request, 'zerar_pontos_classificacao.html')



@login_required(login_url="login/")
def salvar_jogos(request):
    formClear = JogoForm()
    usuario = request.user
    if request.method == "POST":
        comentario = request.POST.get('comentario')
        form = JogoForm(request.POST)
        if form.is_valid():
            jogo = form.save()
            atualizar_classificacao(jogo)
            casa = getattr(jogo, 'time_casa')
            visitante = getattr(jogo, 'time_visitante')
            placar_casa = getattr(jogo, 'placar_casa')
            placar_visitante = getattr(jogo, 'placar_visitante')


            casa_str = str(casa)
            visitante_str = str(visitante)
            request.session['casa'] = casa_str
            request.session['visitante'] = visitante_str
            request.session['placar_casa'] = placar_casa
            request.session['placar_visitante'] = placar_visitante


            mensagem = f'{casa} {placar_casa} x {placar_visitante} {visitante}'
            NotificacaoJogo.objects.create(resultado=mensagem,comentario=f'{usuario}: {comentario}')

            messages.success(request, f'Jogo salvado com sucesso!')
            context = {'form': formClear,}
            return redirect("salvar_gols")

    else:
        form = JogoForm()
         # Filtrar queryset do time_visitante para excluir o time_casa selecionado
        if request.POST.get('time_casa'):
            form.fields['time_visitante'].queryset = form.fields['time_casa'].queryset.exclude(pk=request.POST.get('time_casa'))

    context = {'form': form,}
    return render(request, 'salvar_jogos.html', context)

def salvar_gols_assistencias(request):
    casa = request.session.get('casa')
    visitante = request.session.get('visitante')
    placar_casa = request.session.get('placar_casa')
    placar_visitante = request.session.get('placar_visitante')
    usuario_casa = User.objects.get(username=casa)
    usuario_visitante = User.objects.get(username=visitante)
    jogadores_casa = DadosEafc.objects.filter(time_usuario__usuario=usuario_casa)
    jogadores_visitante = DadosEafc.objects.filter(time_usuario__usuario=usuario_visitante)
    mensagem_resultado = f"{casa} {placar_casa} x {placar_visitante} {visitante}"

    if request.method == "POST":
        jogadores_gols_casa = []
        jogadores_assistencia_casa = []
        jogadores_gols_visitante = []
        jogadores_assistencia_visitante = []
        for i in range(placar_casa):
            jogador_gols_casa = request.POST.get(f"gols_casa_{i}")
            jogador_assistencia_casa = request.POST.get(f"assistencia_casa_{i}")
            jogador_gols_visitante = request.POST.get(f"gols_visitante_{i}")
            jogador_assistencia_visitante = request.POST.get(f"assistencia_visitante_{i}")

            jogadores_gols_casa.append(jogador_gols_casa)
            jogadores_assistencia_casa.append(jogador_assistencia_casa)
            jogadores_gols_visitante.append(jogador_gols_visitante)
            jogadores_assistencia_visitante.append(jogador_assistencia_visitante)


        contagens_gols_casa = contagens_gols_assistencia(jogadores_gols_casa)
        contagens_assistencia_casa = contagens_gols_assistencia(jogadores_assistencia_casa)
        contagens_gols_visitante = contagens_gols_assistencia(jogadores_gols_visitante)
        contagens_assistencia_visitante = contagens_gols_assistencia(jogadores_assistencia_visitante)

        for nomes in contagens_gols_casa.keys():
            if nomes:
                jogador_casa = DadosEafc.objects.get(nome=nomes)
                jogador_casa.gols += contagens_gols_casa[nomes]
                jogador_casa.save()
            else:
                print(f"Error: {nomes}")

        for nomes in contagens_assistencia_casa.keys():
            if nomes:
                jogador_casa = DadosEafc.objects.get(nome=nomes)
                jogador_casa.assistencias += contagens_assistencia_casa[nomes]
                jogador_casa.save()
            else:
                print(f"Error: {nomes}")

        for nomes in contagens_gols_visitante.keys():
            if nomes:
                jogador_visitante = DadosEafc.objects.get(nome=nomes)
                jogador_visitante.gols += contagens_gols_visitante[nomes]
                jogador_visitante.save()
            else:
                print(f"Error: {nomes}")

        for nomes in contagens_assistencia_visitante.keys():
            if nomes:
                jogador_visitante = DadosEafc.objects.get(nome=nomes)
                jogador_visitante.assistencias += contagens_assistencia_visitante[nomes]
                jogador_visitante.save()
            else:
                print(f"Error: {nomes}")


    context = {'jogadores_casa':jogadores_casa,'jogadores_visitante':jogadores_visitante, 'placar_casa':range(placar_casa),'placar_visitante':range(placar_visitante), 'mensagem_resultado':mensagem_resultado}
    return render(request, 'salvar_gols.html', context)

@login_required(login_url="login/")
def leiloes(request):
    jogador_usuario = OrcamentoTime.objects.filter(usuario=request.user)
    posicoes = DadosEafc.objects.values_list('posicao',flat=True).distinct()
    news = News.objects.all().order_by('-date')[:10]
    posicao_selecionada = request.GET.get('posicao')
    nome_pesquisa = request.GET.get('pesquisar')
    if nome_pesquisa:
        jogadores = DadosEafc.objects.filter(nome__icontains=nome_pesquisa)
        leilao,criado = LeilaoAtivo.objects.get_or_create()
        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

        context = {'posts':posts, "leilao_ativo": leilao.ativo, 'jogador_usuario':jogador_usuario,'news': news, 'posicoes':posicoes,"posicao_selecionada": posicao_selecionada}
        return render(request,'leiloes.html',context)

    elif posicao_selecionada:
        jogadores = DadosEafc.objects.filter(posicao=posicao_selecionada)
        leilao,criado = LeilaoAtivo.objects.get_or_create()
        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

        context = {'posts':posts, "leilao_ativo": leilao.ativo, 'jogador_usuario':jogador_usuario,'news': news, 'posicoes':posicoes,"posicao_selecionada": posicao_selecionada}
        return render(request,'leiloes.html',context)

    else:
        nome_jogador = request.session.get('nome_jogador')
        jogadores = DadosEafc.objects.all().order_by('-preco', '-overall')
        leilao,criado = LeilaoAtivo.objects.get_or_create()
        posicao_selecionada = ""
        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)
        if nome_jogador:
            meu_jogador = DadosEafc.objects.get(nome=nome_jogador )
            meu_jogador.preco *= decimal.Decimal(1.05)  # Aumenta o preço em 5%
            meu_jogador.salario = decimal.Decimal(meu_jogador.preco) * decimal.Decimal(0.10) # Aumenta o salario em 5%
            meu_jogador.save()

        if 'nome_jogador' in request.session:
            del request.session['nome_jogador']

        context = {'posts':posts, "leilao_ativo": leilao.ativo, 'jogador_usuario':jogador_usuario,'news': news, 'posicoes':posicoes,"posicao_selecionada": posicao_selecionada}
        return render(request,'leiloes.html',context)


@login_required(login_url="login/")
def comprar_jogador(request, player_id):
    usuario = Usuario.objects.get(usuario=request.user)
    jogador = get_object_or_404(DadosEafc, id=player_id)
    team, created = Team.objects.get_or_create(usuario=request.user)
    jogadores = DadosEafc.objects.filter(time_usuario=team)
    orcamento_time = OrcamentoTime.objects.get(usuario=request.user)
    perfil_comprador = OrcamentoTime.objects.get(usuario=request.user)
    total_jogador_comprador = Team.objects.get(usuario=request.user)
    team.nome = usuario.nome
    time_anterior = jogador.time_usuario

    if jogador.time_usuario == team:
        messages.error(request, 'Você já possui este jogador.')
        return redirect('leiloes')

      # Verifica o número de compras entre o comprador e o vendedor
    # transaction_count = Transaction.objects.filter(buyer=request.user, seller=jogador.time_usuario).count()

    # Verifica se o time do comprador já tem 20 jogadores
    if total_jogador_comprador.jogador.count() > 20:
        messages.error(request, 'Seu time já tem 20 jogadores. Você não pode comprar mais jogadores.')
        return redirect('leiloes')

    # Transação atômica para garantir consistência dos dados
    with transaction.atomic():
        if time_anterior:
            # atribuindo os valores ao antigo dono do jogador ao ser comprado
            dono_anterior = time_anterior.usuario
            perfil_proprietario_anterior = OrcamentoTime.objects.get(usuario=dono_anterior)
            perfil_proprietario_anterior.dinheiro_time += jogador.preco
            perfil_proprietario_anterior.salario_time -= jogador.salario
            # perfil_proprietario_anterior.saldo = (perfil_proprietario_anterior.dinheiro_time - perfil_proprietario_anterior.salario_time)
            perfil_proprietario_anterior.save()

            if perfil_proprietario_anterior.salario_time < 0:
                perfil_proprietario_anterior.salario_time = 0
                perfil_proprietario_anterior.save()


        # verificando se o saldo do usuario é nagativo
        if perfil_comprador.saldo <= jogador.preco:
            messages.error(request, 'Você não tem saldo suficiente para comprar esse jogador!')
            return redirect('leiloes')

            # Define o limite de saldo negativo permitido (até -50% do saldo atual) e o valor do jogador
        valor_total_negativo = decimal.Decimal(perfil_comprador.saldo) * decimal.Decimal(-0.7)
        if perfil_comprador.saldo < valor_total_negativo :
            messages.error(request, 'Você passou do limíte no seu orçamento salárial!')
            return redirect('leiloes')

        # perfil do usuario comprador
        perfil_comprador.dinheiro_time -= jogador.preco
        perfil_comprador.salario_time += jogador.salario
        # perfil_comprador.saldo = (perfil_comprador.dinheiro_time - perfil_comprador.salario_time)
        perfil_comprador.save()

        jogador.time_usuario = team
        jogador.save()
        team.save()

        # Cria a notícia
        if time_anterior:
            news_description = f"{perfil_comprador.usuario} comprou {jogador.nome} de {time_anterior.usuario} por R$ {moeda(jogador.preco)}"
            News.objects.create(buyer=request.user, seller=time_anterior.usuario, player=jogador, description=news_description)
        else:
            valor = jogador.preco
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            valor = locale.currency(valor, grouping=True, symbol=None)
            news_description = f"{perfil_comprador.usuario} comprou {jogador.nome} do Sistema por R$ {moeda(jogador.preco)}"
            News.objects.create(buyer=request.user, seller=None, player=jogador, description=news_description)

        # Registra a transação
        # Transaction.objects.create(buyer=request.user, seller=jogador.time_usuario, player=jogador)

        # Criar notificação
        if time_anterior and time_anterior.usuario != request.user:
            mensagem = f'Seu jogador {jogador.nome} foi comprado por {request.user.username}.'
            notificacao('Arena eSports', mensagem)
            Notificacao.objects.create(usuario=time_anterior.usuario,mensagem=mensagem)

    valor = jogador.preco
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor = locale.currency(valor, grouping=True, symbol=None)
    messages.success(request, f'Você comprou {jogador.nome} por ${valor}')
    request.session['nome_jogador'] = jogador.nome

    salario_total_elenco = sum(jogador.salario for jogador in jogadores)

    orcamento_time.dinheiro_time = perfil_comprador.dinheiro_time
    orcamento_time.salario_time = salario_total_elenco
    # orcamento_time.saldo = orcamento_time.dinheiro_time - orcamento_time.salario_time
    orcamento_time.save()
    return redirect("leiloes")


@login_required(login_url="login/")
def contratar_jogador(request):
    leilao,criado = LeilaoAtivo.objects.get_or_create()
    posicoes = DadosEafc.objects.values_list('posicao',flat=True).distinct()
    nome_pesquisa = request.GET.get('pesquisar')
    posicao_selecionada = request.GET.get('posicao')
    if nome_pesquisa:
        jogadores = DadosEafc.objects.filter(nome__icontains=nome_pesquisa, time_usuario__isnull=True)
        leilao,criado = LeilaoAtivo.objects.get_or_create()
        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

        context = {'posts':posts, "contratacao_ativo": leilao.contratacao_ativo,'posicoes':posicoes}
        return render(request,'contratar.html',context)
    elif posicao_selecionada:
        jogadores = DadosEafc.objects.filter(posicao=posicao_selecionada,  time_usuario__isnull=True)
        leilao,criado = LeilaoAtivo.objects.get_or_create()
        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

        context = {'posts':posts, "contratacao_ativo": leilao.contratacao_ativo,'posicoes':posicoes}
        return render(request,'contratar.html',context)
    else:
        jogadores = jogadores_livre = DadosEafc.objects.filter(time_usuario__isnull=True)
        leilao,criado = LeilaoAtivo.objects.get_or_create()

        #paginator
        paginator = Paginator(jogadores, 20)
        page_obj = request.GET.get('page')
        posts = paginator.get_page(page_obj)

    context = {'posts':posts, "contratacao_ativo": leilao.contratacao_ativo,'posicoes':posicoes}
    return render(request, 'contratar.html', context)



@login_required(login_url="login/")
def contratar_jogador_time(request, id_jogador):
    jogador = get_object_or_404(DadosEafc, id=id_jogador)
    team, created = Team.objects.get_or_create(usuario=request.user)

    if jogador.time_usuario is not None:
        messages.error(request, 'Este jogador já foi contratado por outro time.')
        return redirect('contratar_jogador')

    # Transação atômica para garantir consistência dos dados
    with transaction.atomic():
        perfil_comprador = OrcamentoTime.objects.get(usuario=request.user)

        if perfil_comprador.saldo < jogador.preco:
            messages.error(request, 'Saldo insuficiente.')
            return redirect('contratar_jogador')

        perfil_comprador.dinheiro_time -= jogador.preco
        perfil_comprador.salario_time += jogador.salario
        perfil_comprador.save()

        #associando o jogador ao usuasrio
        jogador.time_usuario = team
        jogador.save()

    messages.success(request, f'Você contratou {jogador.nome} por ${jogador.preco:.2f}')
    return redirect('meu_time')


@login_required(login_url="login/")
def trade_list(request):
    # Obter todas as propostas de troca feitas ou recebidas pelo usuário
    proposals_made = TradeProposal.objects.filter(proposer=request.user).order_by('-created_at')
    proposals_received = TradeProposal.objects.filter(receiver=request.user).order_by('-created_at')

    return render(request, 'trade/trade_list.html', {
        'proposals_made': proposals_made,
        'proposals_received': proposals_received,
    })

@login_required(login_url="login/")
def select_players_for_trade(request):
    # Obtém o time do usuário logado
    user_team = get_object_or_404(Team, usuario=request.user)
    user_players = DadosEafc.objects.filter(time_usuario=user_team)

    # Obtém todos os jogadores que não estão no time do usuário
    other_players = DadosEafc.objects.exclude(time_usuario=user_team).filter(time_usuario__isnull=False)

    if request.method == 'POST':
        proposer_player_id = request.POST.get('proposer_player')
        receiver_player_id = request.POST.get('receiver_player')

        if proposer_player_id and receiver_player_id:
            return redirect('propose_trade', proposer_player_id=proposer_player_id, receiver_player_id=receiver_player_id)
        else:
            messages.error(request, 'Você deve selecionar jogadores para a troca.')

    return render(request, 'trade/select_players_for_trade.html', {
        'user_players': user_players,
        'other_players': other_players,
    })


@login_required(login_url="login/")
def propose_trade(request, proposer_player_id, receiver_player_id):
    proposer_player = get_object_or_404(DadosEafc, id=proposer_player_id)
    receiver_player = get_object_or_404(DadosEafc, id=receiver_player_id)

    # Verificar se os jogadores pertencem aos times dos respectivos usuários
    if proposer_player.time_usuario.usuario != request.user or receiver_player.time_usuario.usuario == request.user:
        messages.error(request, 'Jogadores inválidos para troca.')
        return redirect('player_list')


    if request.method == 'POST':
        money_offered = request.POST.get('money_offered')

        # Criar uma nova proposta de troca
        TradeProposal.objects.create(
            proposer=request.user,
            receiver=receiver_player.time_usuario.usuario,
            proposer_player=proposer_player,
            receiver_player=receiver_player,
            money_offered=money_offered,
        )

        messages.success(request, 'Proposta de troca enviada.')
        return redirect('trade_list')
    context =  {
        'proposer_player': proposer_player,
        'receiver_player': receiver_player,
    }
    return render(request, 'trade/propose_trade.html',context)


@login_required(login_url="login/")
def confirm_trade_proposer(request, trade_id):
    trade = get_object_or_404(TradeProposal, id=trade_id, proposer=request.user)

    if request.method == 'POST':
        trade.confirmed_by_proposer = True
        trade.save()
        messages.success(request, 'Você confirmou a troca. Agora aguarde a confirmação do receptor.')
        return redirect('trade_list')

    return render(request, 'trade/confirm_trade_proposer.html', {'trade': trade})


@login_required(login_url="login/")
def respond_trade(request, trade_id):
    trade = get_object_or_404(TradeProposal, id=trade_id, receiver=request.user)
    print(trade)
    if request.method == 'POST':
        response = request.POST.get('response')
        if response == 'accept':
            # Confirmação do receptor
            trade.confirmed_by_receiver = True
            trade.status = 'accepted'
            trade.save()

            # Executar a troca se ambos confirmaram
            if trade.confirmed_by_proposer and trade.confirmed_by_receiver:
                with transaction.atomic():
                    # Trocar jogadores entre os times
                    proposer_team = trade.proposer_player.time_usuario
                    receiver_team = trade.receiver_player.time_usuario
                    print(proposer_team)
                    print(receiver_team)
                    trade.proposer_player.time_usuario = receiver_team
                    trade.receiver_player.time_usuario = proposer_team

                    trade.proposer_player.save()
                    trade.receiver_player.save()

                    # Ajustar saldos dos usuários
                    proposer_profile = OrcamentoTime.objects.get(usuario=trade.proposer)
                    receiver_profile = OrcamentoTime.objects.get(usuario=trade.receiver)

                    proposer_profile.dinheiro_time += trade.money_offered
                    receiver_profile.dinheiro_time -= trade.money_offered

                    proposer_profile.save()
                    receiver_profile.save()

            messages.success(request, 'Você aceitou a troca.')
        else:
            trade.status = 'rejected'
            trade.save()
            messages.success(request, 'Você rejeitou a troca.')
        return redirect('trade_list')

    return render(request, 'trade/respond_trade.html', {'trade': trade})



@login_required(login_url="login/")
@csrf_exempt
def meu_time(request):
    usuario = Usuario.objects.get(usuario=request.user)
    team, created = Team.objects.get_or_create(usuario=request.user)
    jogadores = DadosEafc.objects.filter(time_usuario=team)
    leilao,criado = LeilaoAtivo.objects.get_or_create()

    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        jogador = get_object_or_404(DadosEafc, id=player_id, time_usuario=team)

        with transaction.atomic():
            # Atualiza o salário do time do usuário
            perfil_usuario = OrcamentoTime.objects.get(usuario=request.user)
            perfil_usuario.salario_time -= jogador.salario
            perfil_usuario.save()

            # Remove o jogador do time
            jogador.time_usuario = None
            jogador.save()

        messages.success(request, f'{jogador.nome} foi dispensado do seu time.')
        return redirect("meu_time")
    # player = OrcamentoTime.objects.all()
    else:
        context = {'jogadores':jogadores, "usuario":usuario, "contratacao_ativo": leilao.contratacao_ativo}
        return render(request,'meu_time.html',context)


@login_required(login_url="login/")
def perfil(request):
    user = request.user
    usuario = Usuario.objects.filter(usuario=user)
    times = TimesEmblemas.objects.all()
    verificado = True
    if request.method == 'POST':
        dados = request.POST.dict()
        nome = dados.get("nome")
        sobrenome = dados.get("sobrenome")
        email = dados.get("email")
        whatsapp = dados.get("whatsapp")
        time = dados.get("time")
        try:
            img = request.FILES['img']
        except KeyError:
            for cliente in usuario:
                img = 'https://crn10.org.br/wp-content/uploads/2021/09/perfil-300x300-4.jpg'
                cliente.save()

        for cliente in usuario:
            cliente.nome = nome
            cliente.sobrenome = sobrenome
            cliente.email = email
            cliente.whatsapp = whatsapp
            cliente.imagem = img
            cliente.emblema_time = time
            cliente.save()

    else:
        for item in usuario:
            if item.email:
                verificado = True
                context = {"dados":usuario, "verificado":verificado,"times":times}
                return render(request, 'perfil.html',context)
            else:
                verificado = False
                context = {"dados":usuario, "verificado":verificado,"times":times}
                return render(request, 'perfil.html',context)

    context = {"dados":usuario, "verificado":verificado}
    return render(request, 'perfil.html',context)


def fazer_login(request):
    error = False
    if request.user.is_authenticated:
        return redirect("homepage")
    if request.method == "POST":
        dados = request.POST.dict()
        if "username" in dados and "senha" in dados:
            username = dados.get("username")
            senha = dados.get("senha")
            usuario = authenticate(request, username=username, password=senha)
            if usuario:
                #fazer o login
                login(request, usuario)
                return redirect("homepage")
            else:
                error = True
                context = {"error":error}
                return render(request,"login.html", context)
        else:
            error = True
    context = {"error": error}
    return render(request,'login.html', context )


def fazer_logout(request):
    logout(request)
    return redirect("login")


def handler404(request, exception):
    return render(request, "pages-error-404.html")
