from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

class UsuarioAdmin(admin.ModelAdmin):
    model = Usuario
    list_display = ["usuario", "email", "whatsapp", "pagamento"]
    search_fields = ["usuario"]
    list_filter = ["usuario"]

class TimeEmblemaAdmin(admin.ModelAdmin):
    model = TimesEmblemas
    list_display = ["time", "emblema"]
    search_fields = ["time"]
    list_filter = ["time"]

class PartidaAdmin(admin.ModelAdmin):
    model = Partida
    list_display = ["time_casa", "time_visitante", "finalizado"]
    search_fields = ["time_casa", "time_visitante"]

class ClassificacaoAdmin(admin.ModelAdmin):
    model = Classificacao
    list_display = ["usuario", "pontos", "jogos", "pagamento"]
    search_fields = ["usuario"]
    list_filter = ["usuario"]

class OrcamentoTimeAdmin(admin.ModelAdmin):
    model = OrcamentoTime
    list_display = ["usuario", "saldo", ]
    search_fields = ["usuario"]
    list_filter = ["usuario"]

class DadosEafcTimeAdmin(admin.ModelAdmin):
    model = DadosEafc
    list_display = ["nome", "overall", "time_usuario", "preco"]
    search_fields = ["time_usuario"]
    list_filter = ["nome"]

class TeamAdmin(admin.ModelAdmin):
    model = Team
    list_display = ["usuario",]
    search_fields = ["nome"]
    list_filter = ["usuario"]


class LeilaoAtivoAdmin(admin.ModelAdmin):
    model = LeilaoAtivo
    list_display = ["ativo", "contratacao_ativo"]
    search_fields = ["ativo"]

class NewsAdmin(admin.ModelAdmin):
    model = News
    list_display = ["buyer", "seller", "player"]
    search_fields = ["buyer"]



admin.site.register(Partida,PartidaAdmin)
admin.site.register(Rodada)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(TimesEmblemas, TimeEmblemaAdmin)
admin.site.register(Classificacao, ClassificacaoAdmin)
admin.site.register(OrcamentoTime, OrcamentoTimeAdmin)
admin.site.register(DadosEafc, DadosEafcTimeAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(LeilaoAtivo, LeilaoAtivoAdmin)
admin.site.register(News,NewsAdmin)
admin.site.register(TradeProposal)
admin.site.register(Notificacao)
admin.site.register(NotificacaoJogo)
