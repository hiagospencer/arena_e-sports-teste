# Generated by Django 5.0.7 on 2024-08-22 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_dadoseafc_preco_alter_dadoseafc_salario'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificacao',
            name='jogos',
            field=models.IntegerField(default=0),
        ),
    ]