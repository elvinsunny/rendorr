# Generated by Django 5.1.1 on 2024-09-29 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_joke_dislikes_remove_joke_likes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joke',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
