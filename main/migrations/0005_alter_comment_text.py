# Generated by Django 4.0.4 on 2022-05-04 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_comment_likes_alter_comment_is_publish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='Оставить свой комментарий'),
        ),
    ]
