# Generated by Django 2.0.2 on 2018-03-22 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RocketAPIAuthentication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rocket_chat_user_id', models.CharField(max_length=100)),
                ('rocket_chat_auth_token', models.CharField(max_length=150)),
                ('rocket_chat_url', models.CharField(max_length=255)),
            ],
        ),
    ]
