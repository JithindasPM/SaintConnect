# Generated by Django 5.0.3 on 2025-01-31 06:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='House_Name',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile_Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('address', models.TextField(null=True)),
                ('age', models.PositiveIntegerField(null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], max_length=100, null=True)),
                ('profile_picture', models.FileField(blank=True, null=True, upload_to='images')),
                ('phone_number', models.PositiveIntegerField(null=True)),
                ('role', models.CharField(choices=[('Member', 'Member'), ('Staff', 'Staff'), ('Youth', 'Youth'), ('Committee Member', 'Committee Member'), ('Choir', 'Choir')], max_length=100, null=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('house_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.house_name')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
