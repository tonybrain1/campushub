# Generated by Django 2.1.1 on 2018-09-25 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_profile_jobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, default='location default text', max_length=120, null=True),
        ),
    ]
