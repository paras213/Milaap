# Generated by Django 2.2.7 on 2020-02-15 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('child', '0009_esehi_perms'),
    ]

    operations = [
        migrations.AddField(
            model_name='esehi',
            name='uperms',
            field=models.IntegerField(default=0),
        ),
    ]