from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedzonko', '0005_auto_20240527_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='preparation_method',
            field=models.CharField(default='test', max_length=255),
            preserve_default=False,
        ),
    ]
