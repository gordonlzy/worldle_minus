from django.db import models

class Continent(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    @classmethod
    def get_default_continents(cls):
        return [
            ('AF', 'Africa'),
            ('AS', 'Asia'),
            ('EU', 'Europe'),
            ('NA', 'North America'),
            ('SA', 'South America'),
            ('OC', 'Oceania'),
            ('PA', 'Pacific Islands'),
            ('CB', 'Caribbean Islands')
        ]

class Country(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='flags/')
    map = models.ImageField(upload_to='maps/', null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    continents = models.ManyToManyField(Continent)
    
    def __str__(self):
        return self.name
    
class GameSession(models.Model):
    session_key = models.CharField(max_length=100)
    current_country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    attempts_left = models.IntegerField(default=5)
    guessed_countries = models.ManyToManyField(Country, related_name='guessed_in_sessions', blank=True)
    selected_continents = models.ManyToManyField(Continent, related_name='used_in_sessions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session {self.session_key} - {self.current_country}"