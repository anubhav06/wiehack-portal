# Generated by Django 4.1.7 on 2023-03-08 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0006_submissionform_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionform',
            name='file',
            field=models.FileField(blank=True, upload_to='uploads/'),
        ),
    ]