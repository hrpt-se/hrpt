# Generated by Django 2.2.16 on 2021-01-27 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0006_replace_hvad_w_parler'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailQueue',
            fields=[
            ],
            options={
                'verbose_name': 'Email queue',
                'verbose_name_plural': 'Email queue',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('reminder.manualnewsletter',),
        ),
    ]