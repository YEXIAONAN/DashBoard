# Generated by Django 5.2.4 on 2025-07-21 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_userinputdishtable_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('calories', models.PositiveIntegerField()),
                ('image_url', models.URLField()),
            ],
            options={
                'db_table': 'dish',
            },
        ),
    ]
