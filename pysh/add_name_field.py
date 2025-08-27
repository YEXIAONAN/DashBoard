from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_dish'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='姓名'),
        ),
    ]