# Generated by Django 2.1.2 on 2018-10-25 04:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_images_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='images',
            name='video',
        ),
    ]