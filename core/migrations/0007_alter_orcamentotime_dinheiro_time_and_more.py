# Generated by Django 5.0.7 on 2024-08-17 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_orcamentotime_dinheiro_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orcamentotime',
            name='dinheiro_time',
            field=models.DecimalField(decimal_places=2, default=30000, max_digits=100),
        ),
        migrations.AlterField(
            model_name='orcamentotime',
            name='saldo',
            field=models.DecimalField(decimal_places=2, default=30000, max_digits=100),
        ),
    ]