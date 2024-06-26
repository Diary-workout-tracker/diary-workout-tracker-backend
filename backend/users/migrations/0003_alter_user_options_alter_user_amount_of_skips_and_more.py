# Generated by Django 5.0.3 on 2024-03-05 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'пользователь', 'verbose_name_plural': 'пользователи'},
        ),
        migrations.AlterField(
            model_name='user',
            name='amount_of_skips',
            field=models.PositiveSmallIntegerField(default=5, verbose_name='Количество доступных пропусков/заморозок'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты'),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('NS', 'Not Set')], default='NS', max_length=2, verbose_name='Пол'),
        ),
        migrations.AlterField(
            model_name='user',
            name='height_cm',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Рост в см'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_completed_training_number',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Последняя завершенная тренировка'),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default=1, max_length=150, verbose_name='Полное имя'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, null=True, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='user',
            name='weight_kg',
            field=models.FloatField(blank=True, null=True, verbose_name='Вес в кг'),
        ),
    ]
