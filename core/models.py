from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Usuario(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    sobrenome = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=200, null=True, blank=True)
    whatsapp = models.CharField(max_length=200, null=True, blank=True)
    pagamento = models.BooleanField(default=False)
    imagem = models.ImageField(upload_to='imagens')
    time = models.CharField(max_length=200, null=True, blank=True)
    emblema_time = models.CharField(max_length=200, null=True, blank=True)


    def __str__(self):
        return f"Nome: {self.usuario}"

class Rodada(models.Model):
    numero = models.IntegerField()

    def __str__(self):
        return f"Rodada {self.numero}"

class Partida(models.Model):
    # rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    time_casa = models.ForeignKey(User, related_name='time_casa', on_delete=models.CASCADE)
    time_visitante = models.ForeignKey(User, related_name='time_visitante', on_delete=models.CASCADE)
    placar_casa = models.IntegerField(blank=True, null=True)
    placar_visitante = models.IntegerField(blank=True, null=True)
    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.time_casa} {self.placar_casa} x {self.placar_visitante} {self.time_visitante}  - Finalizado {self.finalizado}"

class OrcamentoTime(models.Model):
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    dinheiro_time = models.DecimalField(default=200000, max_digits=100, decimal_places=2)
    salario_time = models.DecimalField(default=0, max_digits=100, decimal_places=2)
    saldo = models.DecimalField(default=200000, max_digits=100, decimal_places=2)

    def __Str__(self):
        return f"usuario: {self.usuario} saldo: {self.saldo}"

class Classificacao(models.Model):
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    pontos = models.IntegerField(default=0)
    vitoria = models.IntegerField(default=0)
    empate = models.IntegerField(default=0)
    derrota = models.IntegerField(default=0)
    gols_pro = models.IntegerField(default=0)
    gols_contra = models.IntegerField(default=0)
    saldo_gols = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.usuario} - {self.pontos}"


class Team(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class DadosEafc(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    overall = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.CharField(max_length=200, null=True, blank=True)
    posicao = models.CharField(max_length=200, null=True, blank=True)
    preco = models.DecimalField(default=4000, max_digits=100, decimal_places=2)
    salario = models.DecimalField(default=2000, max_digits=100, decimal_places=2)
    time_usuario = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    comprado = models.BooleanField(default=False)


class TradeProposal(models.Model):
    proposer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals_received')
    proposer_player = models.ForeignKey(DadosEafc, on_delete=models.CASCADE, related_name='proposer_player')
    receiver_player = models.ForeignKey(DadosEafc, on_delete=models.CASCADE, related_name='receiver_player')
    money_offered = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed_by_proposer = models.BooleanField(default=False)
    confirmed_by_receiver = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')


class TimesEmblemas(models.Model):
    time = models.CharField(max_length=200, null=True, blank=True)
    emblema = models.ImageField(upload_to='thumbnail')

    def __str__(self):
        return f"time: {self.time} - Emblema: {self.emblema}"


class Verificacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_verificado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.is_verificado}"


class LeilaoAtivo(models.Model):
    ativo = models.BooleanField(default=False)
    contratacao_ativo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ativo}"
