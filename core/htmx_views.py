from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required


from .models import *



@login_required(login_url="login/")
def load_news(request):
    news = News.objects.order_by('-date')[:10]  # pegar as 10 últimas notícias
    return render(request, 'auxiliar/noticias.html', {'news': news})

def load_notificacao(request):
    notificacoes_nao_lidas = Notificacao.objects.filter(usuario=request.user, lida=False)
    return render(request, 'auxiliar/icon_notificacao.html', {'notificacoes_nao_lidas': notificacoes_nao_lidas})

def ver_notificacoes(request):
    notificacoes_nao_lidas = Notificacao.objects.filter(usuario=request.user, lida=False)
    return render(request, 'notificacoes.html', {'notificacoes_nao_lidas': notificacoes_nao_lidas})


@login_required
def marcar_como_lida(request, notificacao_id):
    notificacao = get_object_or_404(Notificacao, id=notificacao_id, usuario=request.user)
    notificacao.lida = True
    notificacao.save()
    return redirect('homepage')  # Retorna uma resposta vazia para HTMX
