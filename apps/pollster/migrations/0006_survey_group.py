# Generated by Django 2.2.16 on 2021-02-04 11:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
        ('pollster', '0005_col_table_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('all_active', models.BooleanField(default=True)),
                ('from_year', models.PositiveSmallIntegerField(null=True)),
                ('to_year', models.PositiveSmallIntegerField(null=True)),
                ('groups', models.ManyToManyField(related_name='survey_groups', to='auth.Group')),
                ('users', models.ManyToManyField(related_name='survey_groups', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='survey',
            name='group',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='survey', to='pollster.SurveyGroup'),
        ),
    ]
