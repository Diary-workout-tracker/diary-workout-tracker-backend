# Generated by Django 5.0.2 on 2024-03-02 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='full name'),
        ),
    ]
