# Generated by Django 5.0.3 on 2025-02-08 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_death_record_applied_by_alter_death_record_member'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile_model',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
