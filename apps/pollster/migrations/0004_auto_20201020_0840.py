# Generated by Django 2.2.16 on 2020-10-20 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pollster', '0003_auto_20201006_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='object_options',
            field=models.ManyToManyField(limit_choices_to={'question': models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='object_of_rules', to='pollster.Question')}, related_name='object_of_rules', to='pollster.Option'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='subject_options',
            field=models.ManyToManyField(limit_choices_to={'question': models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_of_rules', to='pollster.Question')}, related_name='subject_of_rules', to='pollster.Option'),
        ),
    ]