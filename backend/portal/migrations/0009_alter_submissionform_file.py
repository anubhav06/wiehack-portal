# Generated by Django 4.1.7 on 2023-03-08 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0008_alter_submissionform_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionform',
            name='file',
            field=models.FileField(blank=True, max_length=5000, upload_to=''),
        ),
    ]
