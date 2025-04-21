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
    
    if selected_continents.exists():
        # Filter countries by selected continents
        countries = Country.objects.filter(continents__in=selected_continents).distinct()
    else:
        # No filters, get all countries
        countries = Country.objects.all()
    
    # Exclude already guessed countries
    guessed_countries = game_session.guessed_countries.all()
    if guessed_countries.exists():
        countries = countries.exclude(id__in=guessed_countries.values_list('id', flat=True))
    
    if not countries.exists():
        # If all countries are guessed or no countries match the filter,
        # reset guessed countries and start over
        game_session.guessed_countries.clear()
        if selected_continents.exists():
            countries = Country.objects.filter(continents__in=selected_continents).distinct()
        else:
            countries = Country.objects.all()
    
    # Select a random country
    if countries.exists():
        # Get all countries and shuffle them
        countries_list = list(countries)
        random.shuffle(countries_list)
        game_session.current_country = countries_list[0]
        game_session.save()
    else:
        # No countries available for the selected continents
        game_session.current_country = None
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
            context['country_image'] = game_session.current_country.image.url
            if game_session.current_country.map:
                context['country_map'] = game_session.current_country.map.url
        
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
        
        # Check if this is a give up request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and not request.POST.get('guess'):
            result = {
                'correct': False,
                'country_name': game_session.current_country.name if game_session.current_country else "Unknown",
                'attempts_left': 0,
                'game_over': True,
                'distance': 0,  # Ensure this is defined
                'direction': 'N'  # Ensure this is defined
            }
            return JsonResponse(result)
        
        # This is a guess attempt
        guess = request.POST.get('guess', '').strip().lower()
        current_country = game_session.current_country
        
        if current_country and guess:
            guessed_country = Country.objects.filter(name__iexact=guess).first()
            
            if guessed_country and guessed_country.id == current_country.id:
                # Correct guess
                result = {
                    'correct': True,
                    'country_name': current_country.name,
                    'attempts_left': game_session.attempts_left,
                    'distance': 0,  # Ensure this is defined
                    'direction': 'N'  # Ensure this is defined
                }
                
                # Add to guessed countries
                game_session.guessed_countries.add(current_country)
                
                # Select a new country
                _select_new_country(game_session)
                
                # Reset attempts
                game_session.attempts_left = 5
                game_session.save()
            else:
                # Wrong guess - IMPORTANT: Calculate distance and direction BEFORE checking attempts
                distance = 0
                direction = 'N'
                
                if guessed_country:
                    # Try to calculate distance and direction
                    try:
                        # Check if coordinates exist
                        if (guessed_country.latitude is not None and guessed_country.longitude is not None and 
                            current_country.latitude is not None and current_country.longitude is not None):
                            
                            # Calculate distance and direction
                            distance, direction = calculate_distance_and_direction(
                                guessed_country.latitude,
                                guessed_country.longitude,
                                current_country.latitude,
                                current_country.longitude
                            )
                            distance = round(distance)  # Round to integer
                    except Exception as e:
                        print(f"Error calculating distance: {e}")
                        # Keep default values if calculation fails
                
                # THEN decrement attempts and check if game is over
                game_session.attempts_left -= 1
                game_session.save()
                
                if game_session.attempts_left <= 0:
                    # Out of attempts
                    result = {
                        'correct': False,
                        'country_name': current_country.name,
                        'attempts_left': 0,
                        'game_over': True,
                        'distance': distance,  # Use calculated values
                        'direction': direction  # Use calculated values
                    }
                    
                    # Select a new country
                    _select_new_country(game_session)
                    
                    # Reset attempts
                    game_session.attempts_left = 5
                    game_session.save()
                else:
                    # Still has attempts
                    if guessed_country:
                        result = {
                            'correct': False,
                            'attempts_left': game_session.attempts_left,
                            'game_over': False,
                            'distance': distance,  # Use calculated values
                            'direction': direction  # Use calculated values
                        }
                    else:
                        result = {
                            'correct': False,
                            'attempts_left': game_session.attempts_left,
                            'game_over': False,
                            'error': 'Country not found',
                            'distance': distance,  # Use default
                            'direction': direction  # Use default
                        }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(result)
            
            # For non-AJAX requests, add a message and redirect
            if result.get('correct'):
                request.session['message'] = f"Correct! The country was {result.get('country_name', 'Unknown')}. Try the next one!"
            elif result.get('game_over'):
                request.session['message'] = f"Game over! The country was {result.get('country_name', 'Unknown')}. Try the next one!"
            else:
                if 'error' in result:
                    request.session['message'] = f"{result.get('error', 'Unknown error')}. {result.get('attempts_left', 0)} attempts left."
                else:
                    request.session['message'] = f"Wrong guess! The correct country is {result.get('distance', 0)}km {result.get('direction', 'N')}. {result.get('attempts_left', 0)} attempts left."
            
            return redirect('home')
        
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

        return render(request, 'home.html', {
            'game_session': game_session,
            'continents': Continent.objects.all(),
            'country_name': game_session.current_country.name if game_session.current_country else None,
            'attempts_left': game_session.attempts_left,
        })

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

def guess(request):
    if request.method == 'POST':
        # Get or create game session
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        game_session = GameSession.objects.filter(session_key=session_key).first()
        if not game_session or not game_session.current_country:
            return JsonResponse({'error': 'No active game session'})

        guess = request.POST.get('guess')
        if not guess:
            return JsonResponse({'error': 'No guess provided'})

        try:
            guessed_country = Country.objects.get(name__iexact=guess)
        except Country.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid country name',
                'attempts_left': game_session.attempts_left
            })

        try:
            # Calculate distance and direction
            distance, direction = calculate_distance_and_direction(
                guessed_country.latitude,
                guessed_country.longitude,
                game_session.current_country.latitude,
                game_session.current_country.longitude
            )
        except Exception as e:
            return JsonResponse({
                'error': f'Error calculating distance: {str(e)}',
                'attempts_left': game_session.attempts_left,
                'distance': 0,
                'direction': 'N'  # Default values to prevent undefined
            })

        # Check if the guess is correct
        if guessed_country.id == game_session.current_country.id:
            game_session.guessed_countries.add(guessed_country)
            game_session.save()
            return JsonResponse({
                'correct': True,
                'country_name': game_session.current_country.name,
                'guess': guess,
                'distance': round(distance),
                'direction': direction
            })

        # Add the guess to the session
        game_session.guessed_countries.add(guessed_country)
        game_session.attempts_left -= 1
        game_session.save()

        # Check if game is over
        if game_session.attempts_left <= 0:
            country_name = game_session.current_country.name
            
            # Reset game
            _select_new_country(game_session)
            game_session.attempts_left = 5
            game_session.save()
            
            return JsonResponse({
                'game_over': True,
                'country_name': country_name,
                'guess': guess,
                'distance': round(distance),
                'direction': direction,
                'attempts_left': 0
            })

        return JsonResponse({
            'correct': False,
            'distance': round(distance),
            'direction': direction,
            'attempts_left': game_session.attempts_left,
            'guess': guess
        })

    return JsonResponse({'error': 'Invalid request method'})

