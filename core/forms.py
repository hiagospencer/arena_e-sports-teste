from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

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
        self.fields['time_visitante'].queryset = self.fields['time_casa'].queryset

    def clean(self):
        cleaned_data = super().clean()
        time_casa = cleaned_data.get("time_casa")
        time_visitante = cleaned_data.get("time_visitante")

        if time_casa == time_visitante:
            self.add_error('time_visitante', "O time visitante não pode ser o mesmo que o time da casa.")
