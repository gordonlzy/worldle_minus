import random
import math
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import Country, Continent, GameSession

def calculate_distance_and_direction(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Calculate distance using Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    distance = c * r
    
    # Calculate bearing (direction)
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360  # Normalize to 0-360
    
    # Convert bearing to cardinal direction
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = int((bearing + 22.5) / 45) % 8
    direction = directions[index]
    
    return distance, direction

def _select_new_country(game_session):
    # Get countries based on selected continents filter
    selected_continents = game_session.selected_continents.all()
    
    print(f"Selected continents: {[c.name for c in selected_continents]}")
    
    if selected_continents.exists():
        # Filter countries by selected continents
        countries = Country.objects.filter(continents__in=selected_continents).distinct()
        print(f"Found {countries.count()} countries matching continents filter")
    else:
        # No filters, get all countries
        countries = Country.objects.all()
        print(f"No continent filter, found {countries.count()} total countries")
    
    # Select a random country from the pool regardless of whether it's been guessed before
    if countries.exists():
        # Get all countries and shuffle them
        countries_list = list(countries)
        random.shuffle(countries_list)
        game_session.current_country = countries_list[0]
        print(f"Selected country: {game_session.current_country.name}")
        game_session.save()
    else:
        # No countries available for the selected continents
        game_session.current_country = None
        print("WARNING: No countries found matching filters!")
        game_session.save()

class GetCountriesView(View):
    def get(self, request):
        # Get all country names
        countries = list(Country.objects.values_list('name', flat=True))
        return JsonResponse({'countries': countries})

class HomeView(View):
    def get(self, request):
        # Get all available continents for the filter
        continents = Continent.objects.all()
        
        # Check if a game session exists for this user
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        game_session = GameSession.objects.filter(session_key=session_key).first()
        
        if not game_session:
            # Create a new game session
            game_session = GameSession(session_key=session_key)
            game_session.save()
            
            # Select a random country
            _select_new_country(game_session)
        
        # Get the message from the session and clear it
        message = request.session.pop('message', None)
        
        context = {
            'continents': continents,
            'attempts_left': game_session.attempts_left,
            'selected_continents': game_session.selected_continents.all(),
            'message': message,
        }
        
        # If there's a current country, add its image and map to the context
        if game_session.current_country:
            # Check if the country has an image
            if game_session.current_country.image:
                context['country_image'] = game_session.current_country.image.url
            else:
                # Country doesn't have an image, select a new one
                print(f"WARNING: No image for {game_session.current_country.name}, selecting new country")
                _select_new_country(game_session)
                # Recursive call to try again with a new country
                return self.get(request)
                
            # Check if the country has a map
            if hasattr(game_session.current_country, 'map') and game_session.current_country.map:
                context['country_map'] = game_session.current_country.map.url
            else:
                # Country doesn't have a map, select a new one
                print(f"WARNING: No map for {game_session.current_country.name}, selecting new country")
                _select_new_country(game_session)
                # Recursive call to try again with a new country
                return self.get(request)
        
        return render(request, 'home.html', context)
    
    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            return redirect('home')
        
        game_session = GameSession.objects.filter(session_key=session_key).first()
        if not game_session:
            return redirect('home')
        
        # Check if this is a continent filter request
        if 'filter_continents' in request.POST:
            # Get selected continents
            selected_continent_ids = request.POST.getlist('continents')
            
            # Clear previous selections
            game_session.selected_continents.clear()
            
            # Add new selections
            if selected_continent_ids:
                continents = Continent.objects.filter(id__in=selected_continent_ids)
                game_session.selected_continents.add(*continents)
            
            # Reset the game with a new country based on filters
            game_session.attempts_left = 5
            game_session.guessed_countries.clear()
            _select_new_country(game_session)
            
            return redirect('home')
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Check if this is a "give up" request
            if 'give_up' in request.POST:
                # Make sure we have a current country before accessing its name
                if game_session.current_country:
                    result = {
                        'correct': False,
                        'country_name': game_session.current_country.name,
                        'attempts_left': 0,
                        'game_over': True,
                        'distance': 0,
                        'direction': 'N'
                    }
                    # Reset for new game
                    _select_new_country(game_session)
                    game_session.attempts_left = 5
                    game_session.save()
                else:
                    result = {
                        'error': 'No active country to guess',
                        'attempts_left': game_session.attempts_left
                    }
                return JsonResponse(result)
            
            # This is a guess attempt via AJAX
            guess = request.POST.get('guess', '').strip()
            
            # Validate we have a current country to guess
            if not game_session.current_country:
                return JsonResponse({
                    'error': 'No active country to guess',
                    'attempts_left': game_session.attempts_left
                })
            
            if not guess:
                return JsonResponse({
                    'error': 'No guess provided',
                    'attempts_left': game_session.attempts_left
                })
            
            # Try to find the guessed country
            try:
                guessed_country = Country.objects.get(name__iexact=guess)
            except Country.DoesNotExist:
                return JsonResponse({
                    'error': 'Invalid country name',
                    'attempts_left': game_session.attempts_left,
                    'distance': 0,
                    'direction': 'N'
                })
            
            # Check if correct
            if guessed_country.id == game_session.current_country.id:
                # Correct guess
                result = {
                    'correct': True,
                    'country_name': game_session.current_country.name,
                    'attempts_left': game_session.attempts_left
                }
                
                # Add to guessed countries
                game_session.guessed_countries.add(guessed_country)
                
                # Select a new country
                _select_new_country(game_session)
                
                # Reset attempts
                game_session.attempts_left = 5
                game_session.save()
                
                return JsonResponse(result)
            
            # Wrong guess - calculate distance and direction
            distance = 0
            direction = 'N'
            
            try:
                # Check if coordinates exist for both countries
                if (guessed_country.latitude is not None and 
                    guessed_country.longitude is not None and 
                    game_session.current_country.latitude is not None and 
                    game_session.current_country.longitude is not None):
                    
                    # Calculate distance and direction
                    distance, direction = calculate_distance_and_direction(
                        guessed_country.latitude,
                        guessed_country.longitude,
                        game_session.current_country.latitude,
                        game_session.current_country.longitude
                    )
                    distance = round(distance)  # Round to integer
            except Exception as e:
                print(f"Error calculating distance: {e}")
                # Use default values if calculation fails
            
            # Decrement attempts and check if game is over
            game_session.attempts_left -= 1
            game_session.save()
            
            if game_session.attempts_left <= 0:
                # Out of attempts
                result = {
                    'correct': False,
                    'country_name': game_session.current_country.name,
                    'attempts_left': 0,
                    'game_over': True,
                    'distance': distance,
                    'direction': direction
                }
                
                # Select a new country and reset attempts
                _select_new_country(game_session)
                game_session.attempts_left = 5
                game_session.save()
            else:
                # Still has attempts
                result = {
                    'correct': False,
                    'attempts_left': game_session.attempts_left,
                    'game_over': False,
                    'distance': distance,
                    'direction': direction
                }
            
            return JsonResponse(result)
        
        # This is a non-AJAX form submission (rare but possible)
        guess = request.POST.get('guess', '').strip()
        
        if not game_session.current_country or not guess:
            return redirect('home')
        
        try:
            guessed_country = Country.objects.get(name__iexact=guess)
        except Country.DoesNotExist:
            request.session['message'] = "Invalid country name. Please try again."
            return redirect('home')
        
        if guessed_country.id == game_session.current_country.id:
            # Correct guess
            request.session['message'] = f"Correct! The country was {game_session.current_country.name}. Try the next one!"
            
            # Add to guessed countries
            game_session.guessed_countries.add(guessed_country)
            
            # Select a new country
            _select_new_country(game_session)
            
            # Reset attempts
            game_session.attempts_left = 5
            game_session.save()
        else:
            # Wrong guess
            distance = 0
            direction = 'N'
            
            try:
                if (guessed_country.latitude is not None and 
                    guessed_country.longitude is not None and 
                    game_session.current_country.latitude is not None and 
                    game_session.current_country.longitude is not None):
                    
                    distance, direction = calculate_distance_and_direction(
                        guessed_country.latitude,
                        guessed_country.longitude,
                        game_session.current_country.latitude,
                        game_session.current_country.longitude
                    )
                    distance = round(distance)
            except Exception as e:
                print(f"Error calculating distance: {e}")
            
            game_session.attempts_left -= 1
            game_session.save()
            
            if game_session.attempts_left <= 0:
                request.session['message'] = f"Game over! The country was {game_session.current_country.name}. Try the next one!"
                
                # Select a new country
                _select_new_country(game_session)
                
                # Reset attempts
                game_session.attempts_left = 5
                game_session.save()
            else:
                request.session['message'] = f"Wrong guess! The correct country is {distance}km {direction}. {game_session.attempts_left} attempts left."
        
        return redirect('home')

class NewGameView(View):
    def get(self, request):
        session_key = request.session.session_key
        if not session_key:
            return redirect('home')

        game_session = GameSession.objects.filter(session_key=session_key).first()
        if not game_session:
            return redirect('home')

        selected_continent_names = request.GET.getlist('continents')
        if selected_continent_names:
            # Clear previous selections
            game_session.selected_continents.clear()

            # Add new selected continents by name
            selected_continents = Continent.objects.filter(name__in=selected_continent_names)
            game_session.selected_continents.add(*selected_continents)

            # Reset the game session
            game_session.attempts_left = 5
            game_session.guessed_countries.clear()

            # Select a new country based on the selected continents
            _select_new_country(game_session)

        return redirect('home')

    def post(self, request):
        session_key = request.session.session_key
        if not session_key:
            return redirect('home')

        game_session = GameSession.objects.filter(session_key=session_key).first()
        if not game_session:
            return redirect('home')

        # Reset the game session
        game_session.attempts_left = 5
        game_session.guessed_countries.clear()
        _select_new_country(game_session)

        return redirect('home')