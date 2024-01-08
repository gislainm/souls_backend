# Generated by Django 5.0 on 2024-01-01 01:28

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=200, unique=True)),
                ('password', models.CharField(blank=True, max_length=100)),
                ('telephone', models.CharField(blank=True, max_length=100)),
                ('isAdmin', models.BooleanField(default=False)),
            ],
        ),
    ]
