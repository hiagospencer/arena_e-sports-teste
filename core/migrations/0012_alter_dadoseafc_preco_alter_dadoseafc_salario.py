# Generated by Django 5.0.7 on 2024-08-21 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_notificacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadoseafc',
            name='preco',
            field=models.DecimalField(decimal_places=2, default=2000, max_digits=100),
        ),
        migrations.AlterField(
            model_name='dadoseafc',
            name='salario',
            field=models.DecimalField(decimal_places=2, default=200, max_digits=100),
        ),
    ]
