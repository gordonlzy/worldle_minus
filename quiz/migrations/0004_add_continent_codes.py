from django.db import migrations, models

def add_continent_codes(apps, schema_editor):
    Continent = apps.get_model('quiz', 'Continent')
    name_to_code = {
        'Africa': 'AF',
        'Asia': 'AS',
        'Europe': 'EU',
        'North America': 'NA',
        'South America': 'SA',
        'Oceania': 'OC',
        'Pacific Islands': 'PA',
        'Caribbean Islands': 'CB'
    }
    
    # First, clear any existing codes
    Continent.objects.all().update(code=None)
    
    # Then add the codes
    for continent in Continent.objects.all():
        if continent.name in name_to_code:
            continent.code = name_to_code[continent.name]
            continent.save()

def reverse_add_continent_codes(apps, schema_editor):
    Continent = apps.get_model('quiz', 'Continent')
    Continent.objects.all().update(code=None)

class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0003_country_map_alter_country_continents_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='continent',
            name='code',
            field=models.CharField(max_length=2, null=True, blank=True),
        ),
        migrations.RunPython(add_continent_codes, reverse_add_continent_codes),
        migrations.AlterField(
            model_name='continent',
            name='code',
            field=models.CharField(max_length=2, unique=True),
        ),
    ] 