# Generated by Django 5.2.3 on 2025-06-23 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_badgerecords_unlocked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='habit_streak',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='total_checkins',
        ),
    ]
