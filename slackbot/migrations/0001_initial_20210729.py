# Generated by Django 3.1.5 on 2021-07-29 08:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='SlackUser',
            fields=[
                ('user_ptr', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('ext_id', models.CharField(max_length=20)),
                ('is_bot', models.BooleanField(db_index=True, default=False)),
                ('is_admin', models.BooleanField(db_index=True, default=False)),
                ('photo_thumb', models.CharField(blank=True, max_length=255, null=True)),
                ('photo', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnalyticsBot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('message', models.TextField(blank=True, null=True)),
                ('team', models.CharField(db_index=True, editable=False, max_length=100, null=True)),
                ('channel', models.CharField(db_index=True, editable=False, max_length=100, null=True)),
                ('ts', models.CharField(editable=False, max_length=150, null=True)),
                (
                    'user',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='slackbot.slackuser'
                    ),
                ),
            ],
            options={
                'verbose_name': 'Analytics - Slack',
                'verbose_name_plural': 'Analytics - Slack',
            },
        ),
    ]
