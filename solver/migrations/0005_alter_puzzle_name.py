# Generated by Django 4.2.16 on 2024-10-11 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solver', '0004_puzzle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='name',
            field=models.CharField(default='Default', max_length=100),
        ),
    ]
