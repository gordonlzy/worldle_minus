from django.core.management.base import BaseCommand
from quiz.models import Continent

class Command(BaseCommand):
    help = 'Load initial continents data'

    def handle(self, *args, **kwargs):
        continents = [
            'Africa',
            'Antarctica',
            'Asia',
            'Europe',
            'North America',
            'Oceania',
            'South America',
        ]
        
        for continent_name in continents:
            Continent.objects.get_or_create(name=continent_name)
            
        self.stdout.write(self.style.SUCCESS('Successfully loaded continents'))