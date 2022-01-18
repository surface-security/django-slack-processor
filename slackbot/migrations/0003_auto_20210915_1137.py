# Generated by Django 3.1.5 on 2021-09-15 11:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('slackbot', '0002_delete_analyticsbot'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ext_id', models.CharField(max_length=20, unique=True)),
                ('username', models.CharField(max_length=255)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                ('photo_thumb', models.CharField(blank=True, max_length=255, null=True)),
                ('photo', models.CharField(blank=True, max_length=255, null=True)),
                ('is_bot', models.BooleanField(db_index=True, default=False)),
                ('is_admin', models.BooleanField(db_index=True, default=False)),
                ('active', models.BooleanField(default=True)),
                ('last_seen', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.DeleteModel(
            name='SlackUser',
        ),
    ]
