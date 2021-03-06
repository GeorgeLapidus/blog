# Generated by Django 4.0.4 on 2022-05-17 06:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['created'], 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AlterField(
            model_name='answercomment',
            name='is_publish',
            field=models.BooleanField(default=False, verbose_name='Опубликовать'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='is_publish',
            field=models.BooleanField(default=False, verbose_name='Опубликовать'),
        ),
        migrations.AlterField(
            model_name='postadditionalimage',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.post', verbose_name='Новость'),
        ),
    ]
