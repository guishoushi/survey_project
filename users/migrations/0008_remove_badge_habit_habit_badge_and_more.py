# Generated by Django 5.2.3 on 2025-06-23 02:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_badge_habit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badge',
            name='habit',
        ),
        migrations.AddField(
            model_name='habit',
            name='badge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='habits', to='users.badge', verbose_name='关联的徽章'),
        ),
        migrations.AlterField(
            model_name='badgerecords',
            name='badge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badge_records', to='users.badge', verbose_name='徽章'),
        ),
        migrations.AlterField(
            model_name='badgerecords',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='badge_records', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AlterField(
            model_name='checkin',
            name='habit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to='users.habit', verbose_name='习惯'),
        ),
        migrations.AlterField(
            model_name='checkin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
    ]
