from django.contrib.auth.models import AnonymousUser

from .models import Notificacao


def notificacao(request):
    notificacoes_dict = {}
    if isinstance(request.user, AnonymousUser):
        usuario = None
    else:
        usuario = request.user.id
        notificacoes_nao_lidas = Notificacao.count_unread(usuario)
        total_notificacoes = Notificacao.count_all(usuario)
        notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False).order_by('-criada_em')[:4]
        notificacoes_dict = {
            'notificacoes': notificacoes, 'notificacoes_nao_lidas': notificacoes_nao_lidas,
                'total_notificacoes': total_notificacoes,}

    return notificacoes_dict
