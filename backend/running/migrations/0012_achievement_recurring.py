# Generated by Django 5.0.3 on 2024-04-01 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('running', '0011_remove_achievement_black_white_icon_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='recurring',
            field=models.BooleanField(db_comment='Повторяющееся ли достижение', default=False, help_text='Повторяющееся ли достижение', verbose_name='Повторяющееся'),
        ),
    ]
