# Generated by Django 4.1.7 on 2023-05-21 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0018_user_team_type_offline'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='team_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
