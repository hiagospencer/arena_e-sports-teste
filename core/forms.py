from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

from .models import *


class JogoForm(forms.ModelForm):
    class Meta:
        model = Partida
        fields = ['time_casa', 'time_visitante', 'placar_casa', 'placar_visitante']

    def __init__(self, *args, **kwargs):
        super(JogoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Inserir Resultado do Jogo',
                'time_casa',
                'time_visitante',
                'placar_casa',
                'placar_visitante',
            ),
            ButtonHolder(
                Submit('submit', 'Salvar', css_class='btn btn-primary')
            )
        )
        times_ativo = Usuario.objects.filter(pagamento=False)
        self.fields['time_visitante'].queryset = times_ativo
        self.fields['time_casa'].queryset = times_ativo

    def clean(self):
        cleaned_data = super().clean()
        time_casa = cleaned_data.get("time_casa")
        time_visitante = cleaned_data.get("time_visitante")

        if time_casa == time_visitante:
            self.add_error('time_visitante', "O time visitante não pode ser o mesmo que o time da casa.")

        # Contar o número de partidas entre os jogadores
        num_partidas = Partida.objects.filter(
            Q(time_casa=time_casa, time_visitante=time_visitante) |
            Q(time_casa=time_visitante, time_visitante=time_casa)
        ).count()

        if num_partidas >= 2:
            self.add_error('time_visitante', "Os jogadores já se enfrentaram duas vezes.")

        return cleaned_data
