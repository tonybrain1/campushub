# Generated by Django 2.1.2 on 2018-10-25 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20181025_0600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
    ]