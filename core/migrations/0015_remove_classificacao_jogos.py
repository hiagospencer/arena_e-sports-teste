# Generated by Django 5.0.7 on 2024-08-23 17:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_notificacaojogo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classificacao',
            name='jogos',
        ),
    ]
