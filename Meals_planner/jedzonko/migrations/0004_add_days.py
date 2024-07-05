# 0005_add_days.py

from django.db import migrations, models

def add_days(apps, schema_editor):
    DayName = apps.get_model('jedzonko', 'DayName')
    days = [
        {'name': 'Poniedziałek', 'order': 1},
        {'name': 'Wtorek', 'order': 2},
        {'name': 'Środa', 'order': 3},
        {'name': 'Czwartek', 'order': 4},
        {'name': 'Piątek', 'order': 5},
        {'name': 'Sobota', 'order': 6},
        {'name': 'Niedziela', 'order': 7},
    ]
    for day in days:
        DayName.objects.create(**day)

class Migration(migrations.Migration):

    dependencies = [
        ('jedzonko', '0003_page'),  # Upewnij się, że zależność jest poprawna
    ]

    operations = [
        migrations.RunPython(add_days),
    ]
