# Generated by Django 4.1.7 on 2023-03-12 16:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0015_delete_usersession'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='eligible_teams',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]