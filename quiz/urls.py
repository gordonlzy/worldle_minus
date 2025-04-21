from django.urls import path
from .views import HomeView, NewGameView, GetCountriesView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('new-game/', NewGameView.as_view(), name='new_game'),
    path('get-countries/', GetCountriesView.as_view(), name='get_countries'),
]