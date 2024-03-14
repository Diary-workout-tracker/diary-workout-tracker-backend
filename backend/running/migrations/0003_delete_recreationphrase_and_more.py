# Generated by Django 5.0.3 on 2024-03-11 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('running', '0002_history_user_id_alter_achievement_reward_points'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RecreationPhrase',
        ),
        migrations.AlterModelOptions(
            name='motivationalphrase',
            options={'verbose_name': 'Мотивационная фраза', 'verbose_name_plural': 'Мотивационные фразы'},
        ),
        migrations.AddField(
            model_name='motivationalphrase',
            name='rest',
            field=models.BooleanField(db_comment='Флаг, обозначающий фразу отдыха.', default=False, help_text='Флаг, обозначающий фразу отдыха.', verbose_name='Флаг фразы отдыха'),
        ),
        migrations.AlterField(
            model_name='motivationalphrase',
            name='text',
            field=models.TextField(db_comment='Текст фразы.', help_text='Текст фразы.', verbose_name='Текст фразы'),
        ),
    ]