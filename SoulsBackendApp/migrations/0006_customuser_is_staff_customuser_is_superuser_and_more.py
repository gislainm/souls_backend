# Generated by Django 5.0 on 2024-01-11 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SoulsBackendApp', '0005_alter_customuser_is_admin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_group_leader',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='CustomToken',
        ),
    ]
