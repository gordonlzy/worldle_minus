from django.contrib import admin
from .models import Country, Continent, GameSession

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_continents')
    search_fields = ('name',)
    filter_horizontal = ('continents',)
    
    def get_continents(self, obj):
        return ", ".join([c.name for c in obj.continents.all()])
    get_continents.short_description = 'Continents'

@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'current_country', 'attempts_left', 'created_at')
    list_filter = ('created_at',)