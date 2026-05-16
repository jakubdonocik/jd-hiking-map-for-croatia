from django.http import JsonResponse
from django.http import HttpResponse
from django.db import connection
from django.core.serializers import serialize
from .models import Obiekt, Szlak
from django.contrib.auth.decorators import login_required, user_passes_test
import gpxpy
from django.contrib.gis.geos import LineString
from .models import Szlak
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.gis.geos import Point
import json
import requests
from django.core.serializers.json import DjangoJSONEncoder
from .models import (
    Obiekt,
    RodzajObiektu,
    Region,
    Miejscowosc,
    Wezel  
)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import UzytkownikPro
import heapq
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Wezel, Szlak, WezelSzlaku


def is_admin(user):
    return user.is_authenticated and user.is_staff

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

def mapa_view(request):
    return render(request, 'mapa/mapa.html')

def regiony_geojson(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(ST_Force2D(lokalizacja))::jsonb,
                        'properties', jsonb_build_object(
                            'nazwa', nazwa
                        )
                    )
                )
            )
            FROM regiony;
        """)
        geojson = cursor.fetchone()[0]

    return HttpResponse(geojson, content_type='application/json')

def obiekty_geojson(request):
    """Zwraca obiekty jako GeoJSON z informacją o rodzaju"""
    obiekty = Obiekt.objects.select_related('rodzaj_obiektu').all()
    
    features = []
    for obiekt in obiekty:
        if obiekt.lokalizacja:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [obiekt.lokalizacja.x, obiekt.lokalizacja.y]
                },
                'properties': {
                    'nazwa_obiektu': obiekt.nazwa_obiektu,
                    'rodzaj': obiekt.rodzaj_obiektu.rodzaj_obiektu if obiekt.rodzaj_obiektu else 'brak'
                }
            })
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return JsonResponse(geojson)

def szlaki_geojson(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(ST_Force2D(przebieg))::jsonb,
                        'properties', jsonb_build_object(
                            'kolor', kolor,
                            'dlugosc', dlugosc
                        )
                    )
                )
            )
            FROM szlaki;
        """)
        geojson = cursor.fetchone()[0]

    return HttpResponse(geojson, content_type='application/json')

def wezly_geojson(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', COALESCE(jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(
                            ST_Transform(o.lokalizacja, 4326)
                        )::jsonb,
                        'properties', jsonb_build_object(
                            'id', w.id,
                            'nazwa', o.nazwa_obiektu
                        )
                    )
                ), '[]'::jsonb)
            )
            FROM wezly w
            JOIN obiekty o ON o.id = w.id_obiektu;
        """)
        geojson = cursor.fetchone()[0]
    
    return HttpResponse(geojson, content_type='application/json')


@user_passes_test(is_admin)
def dodaj_szlak(request):
    if request.method == 'POST':
        gpx_file = request.FILES['gpx_file']
        kolor = request.POST['kolor']
        start_szlaku_id = request.POST['start_szlaku']
        koniec_szlaku_id = request.POST['koniec_szlaku']
        
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((
                        point.longitude,
                        point.latitude,
                        point.elevation or 0
                    ))
        
        linia = LineString(points, srid=4326)
        
        Szlak.objects.create(
            kolor=kolor,
            start_szlaku_id=start_szlaku_id,
            koniec_szlaku_id=koniec_szlaku_id,
            przebieg=linia
        )
        
        messages.success(request, 'Szlak został dodany pomyślnie!')
        return redirect('/')
    
    wezly = Wezel.objects.select_related('id_obiektu').all()
    
    wezly_json = json.dumps([
        {
            'id': w.id,
            'nazwa': w.id_obiektu.nazwa_obiektu if w.id_obiektu else f'Węzeł {w.id}'
        }
        for w in wezly
    ], cls=DjangoJSONEncoder)
    
    return render(request, 'mapa/dodaj_szlak.html', {
        'wezly': wezly,
        'wezly_json': wezly_json
    })

@login_required
@user_passes_test(is_admin)
def dodaj_obiekt(request):
    if request.method == 'POST':
        nazwa = request.POST['nazwa']
        opis = request.POST['opis']
        rodzaj_id = request.POST['rodzaj']
        lat = float(request.POST['lat'])
        lon = float(request.POST['lon'])
        elevation = float(request.POST.get('elevation', 0))

        rodzaj = RodzajObiektu.objects.get(id=rodzaj_id)

        obiekt = Obiekt.objects.create(
            nazwa_obiektu=nazwa,
            opis=opis,
            rodzaj_obiektu=rodzaj,
            lokalizacja=Point(lon, lat, elevation, srid=4326)
        )

        return redirect('/')

    rodzaje = RodzajObiektu.objects.all()

    return render(
        request,
        'mapa/dodaj_obiekt.html',
        {'rodzaje': rodzaje}
    )
   

@user_passes_test(is_admin)
def lista_szlakow(request):
    """Widok listy wszystkich szlaków"""
    szlaki = Szlak.objects.select_related('start_szlaku__id_obiektu', 'koniec_szlaku__id_obiektu').all()
    return render(request, 'mapa/lista_szlakow.html', {'szlaki': szlaki})


@user_passes_test(is_admin)
def usun_szlak(request, szlak_id):
    """Usuwanie szlaku"""
    if request.method == 'POST':
        try:
            szlak = Szlak.objects.get(id=szlak_id)
            szlak.delete()
            messages.success(request, f'Szlak {szlak_id} został usunięty!')
        except Szlak.DoesNotExist:
            messages.error(request, 'Szlak nie istnieje!')
        return redirect('lista_szlakow')
    
    return redirect('lista_szlakow')


def szlaki_lista_json(request):
    """API endpoint zwracający listę szlaków jako JSON dla panelu bocznego"""
    szlaki = Szlak.objects.select_related('start_szlaku__id_obiektu', 'koniec_szlaku__id_obiektu').all()
    
    data = []
    for szlak in szlaki:
        data.append({
            'id': szlak.id,
            'kolor': szlak.kolor,
            'start': szlak.start_szlaku.id_obiektu.nazwa_obiektu if szlak.start_szlaku and szlak.start_szlaku.id_obiektu else 'N/A',
            'koniec': szlak.koniec_szlaku.id_obiektu.nazwa_obiektu if szlak.koniec_szlaku and szlak.koniec_szlaku.id_obiektu else 'N/A',
            'dlugosc': szlak.dlugosc,
            'suma_podejsc': szlak.suma_podejsc,
            'suma_zejs': szlak.suma_zejs
        })
    
    return JsonResponse(data, safe=False)

def obiekty_lista_json(request):
    """API endpoint zwracający listę obiektów jako JSON"""
    obiekty = Obiekt.objects.select_related('rodzaj_obiektu', 'miejscowosc', 'region').all()
    
    data = []
    for obiekt in obiekty:
        data.append({
            'id': obiekt.id,
            'nazwa': obiekt.nazwa_obiektu,
            'rodzaj': obiekt.rodzaj_obiektu.rodzaj_obiektu if obiekt.rodzaj_obiektu else 'N/A',
            'miejscowosc': obiekt.miejscowosc.nazwa if obiekt.miejscowosc else 'N/A',
            'region': obiekt.region.nazwa if obiekt.region else 'N/A',
            'opis': obiekt.opis or 'Brak opisu'
        })
    
    return JsonResponse(data, safe=False)


@user_passes_test(is_admin)
def usun_obiekt(request, obiekt_id):
    """Usuwanie obiektu"""
    print(f"=== USUWANIE OBIEKTU {obiekt_id} ===")
    print(f"Metoda: {request.method}")
    print(f"Użytkownik: {request.user}")
    
    if request.method == 'POST':
        try:
            obiekt = Obiekt.objects.get(id=obiekt_id)
            nazwa = obiekt.nazwa_obiektu
            print(f"Znaleziono obiekt: {nazwa}")
            
            wezly_usuniete = Wezel.objects.filter(id_obiektu=obiekt_id).delete()
            print(f"Usunięto węzłów: {wezly_usuniete}")
            
            obiekt.delete()
            print(f"Obiekt {nazwa} usunięty!")
            
            return JsonResponse({'status': 'ok'})
        except Obiekt.DoesNotExist:
            print("Obiekt nie istnieje!")
            return JsonResponse({'status': 'error', 'message': 'Nie istnieje'}, status=404)
        except Exception as e:
            print(f"Błąd: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    print("Nieprawidłowa metoda!")
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@user_passes_test(is_admin)
def edytuj_obiekt(request, obiekt_id):

    """Edycja obiektu"""
    try:
        obiekt = Obiekt.objects.select_related('rodzaj_obiektu').get(id=obiekt_id)
    except Obiekt.DoesNotExist:
        messages.error(request, 'Obiekt nie istnieje!')
        return redirect('mapa')
    
    if request.method == 'POST':
        nazwa = request.POST['nazwa']
        opis = request.POST['opis']
        rodzaj_id = request.POST['rodzaj']
        lat = float(request.POST['lat'])
        lon = float(request.POST['lon'])
        elevation = float(request.POST.get('elevation', 0))

        rodzaj = RodzajObiektu.objects.get(id=rodzaj_id)

        obiekt.nazwa_obiektu = nazwa
        obiekt.opis = opis
        obiekt.rodzaj_obiektu = rodzaj
        obiekt.lokalizacja = Point(lon, lat, elevation, srid=4326)
        obiekt.save()

        messages.success(request, f'Obiekt "{nazwa}" został zaktualizowany!')
        return redirect('mapa')

    rodzaje = RodzajObiektu.objects.all()
    
    lat = obiekt.lokalizacja.y if obiekt.lokalizacja else 0
    lon = obiekt.lokalizacja.x if obiekt.lokalizacja else 0
    elevation = obiekt.lokalizacja.z if obiekt.lokalizacja and hasattr(obiekt.lokalizacja, 'z') else 0

    return render(
        request,
        'mapa/edytuj_obiekt.html',
        {
            'obiekt': obiekt,
            'rodzaje': rodzaje,
            'lat': lat,
            'lon': lon,
            'elevation': elevation
        }
    )


def pobierz_wysokosc(request):
    """Proxy do pobierania wysokości"""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({'error': 'Brak współrzędnych'}, status=400)
    
    try:
        url = f'https://api.opentopodata.org/v1/eudem25m?locations={lat},{lon}'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            elevation = round(data['results'][0]['elevation'])
            return JsonResponse({'elevation': elevation})
        else:
            url2 = f'https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}'
            response2 = requests.get(url2, timeout=5)
            data2 = response2.json()
            elevation = round(data2['results'][0]['elevation'])
            return JsonResponse({'elevation': elevation})
            
    except Exception as e:
        print(f'Błąd pobierania wysokości: {e}')
        return JsonResponse({'elevation': 0})


class RegisterForm(forms.Form):
    imie = forms.CharField(max_length=100, label='Imię')
    nazwisko = forms.CharField(max_length=100, label='Nazwisko')
    email = forms.EmailField(label='Email')
    haslo = forms.CharField(widget=forms.PasswordInput, label='Hasło')
    haslo2 = forms.CharField(widget=forms.PasswordInput, label='Powtórz hasło')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ten email jest już zarejestrowany!')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        haslo = cleaned_data.get('haslo')
        haslo2 = cleaned_data.get('haslo2')
        
        if haslo and haslo2 and haslo != haslo2:
            raise forms.ValidationError('Hasła nie są identyczne!')
        
        return cleaned_data


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['haslo'],
                first_name=form.cleaned_data['imie'],
                last_name=form.cleaned_data['nazwisko']
            )
            
            pro_group, created = Group.objects.get_or_create(name='pro')
            user.groups.add(pro_group)
            
            UzytkownikPro.objects.create(
                imie=form.cleaned_data['imie'],
                nazwisko=form.cleaned_data['nazwisko'],
                email=form.cleaned_data['email'],
                haslo=''  
            )
            
            messages.success(request, 'Konto zostało utworzone!')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'mapa/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Witaj, {user.first_name}!')
                return redirect('mapa')
    else:
        form = AuthenticationForm()
    
    return render(request, 'mapa/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Zostałeś wylogowany.')
    return redirect('mapa')


def graf_wezlow(request):
    """
    Zwraca graf węzłów ze szlakami 
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.id,
                s.start_szlaku,
                s.koniec_szlaku,
                s.dlugosc,
                ST_AsGeoJSON(s.przebieg)::json as geometria,
                o_start.nazwa_obiektu as nazwa_start,
                o_koniec.nazwa_obiektu as nazwa_koniec
            FROM szlaki s
            JOIN wezly w_start ON s.start_szlaku = w_start.id
            JOIN wezly w_koniec ON s.koniec_szlaku = w_koniec.id
            JOIN obiekty o_start ON w_start.id_obiektu = o_start.id
            JOIN obiekty o_koniec ON w_koniec.id_obiektu = o_koniec.id
        """)
        
        szlaki = []
        for row in cursor.fetchall():
            szlaki.append({
                'id': row[0],
                'start': row[1],
                'koniec': row[2],
                'dlugosc': row[3] or 0,
                'geometria': row[4],
                'nazwa_start': row[5],
                'nazwa_koniec': row[6]
            })
        
        cursor.execute("""
            SELECT 
                w.id,
                o.nazwa_obiektu,
                ST_X(o.lokalizacja) as lon,
                ST_Y(o.lokalizacja) as lat
            FROM wezly w
            JOIN obiekty o ON w.id_obiektu = o.id
        """)
        
        wezly = []
        for row in cursor.fetchall():
            wezly.append({
                'id': row[0],
                'nazwa': row[1],
                'lon': row[2],
                'lat': row[3]
            })
    
    return JsonResponse({
        'wezly': wezly,
        'szlaki': szlaki
    })
    
def dijkstra(start_id, end_id):
    graf = {}

    for rel in WezelSzlaku.objects.select_related('wezel', 'szlak'):
        graf.setdefault(rel.wezel.id, []).append(rel.szlak)

    kolejka = [(0, start_id, [])]
    odwiedzone = set()

    while kolejka:
        koszt, aktualny, sciezka = heapq.heappop(kolejka)

        if aktualny in odwiedzone:
            continue
        odwiedzone.add(aktualny)

        if aktualny == end_id:
            return sciezka

        for szlak in graf.get(aktualny, []):
            relacje = WezelSzlaku.objects.filter(szlak=szlak)
            for r in relacje:
                if r.wezel.id != aktualny:
                    heapq.heappush(
                        kolejka,
                        (
                            koszt + szlak.dlugosc,
                            r.wezel.id,
                            sciezka + [szlak]
                        )
                    )

    return []




@csrf_exempt
def wyznacz_trase(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body)
    start = data.get('from')
    end = data.get('to')

    szlaki = dijkstra(start, end)

    if not szlaki:
        return JsonResponse({'error': 'Brak trasy'}, status=404)

    response = {
        'szlaki': [],
        'stats': {
            'dlugosc': 0,
            'suma_podejsc': 0,
            'suma_zejs': 0
        }
    }

    for s in szlaki:
        response['szlaki'].append({
            'geometry': json.loads(s.przebieg.geojson)
        })
        response['stats']['dlugosc'] += s.dlugosc or 0
        response['stats']['suma_podejsc'] += s.suma_podejsc or 0
        response['stats']['suma_zejs'] += s.suma_zejs or 0

    return JsonResponse(response)

@user_passes_test(is_admin)
def edytuj_szlak(request, szlak_id):
    """Edycja szlaku"""
    try:
        szlak = Szlak.objects.select_related('start_szlaku__id_obiektu', 'koniec_szlaku__id_obiektu').get(id=szlak_id)
    except Szlak.DoesNotExist:
        messages.error(request, 'Szlak nie istnieje!')
        return redirect('mapa')
    
    if request.method == 'POST':
        kolor = request.POST['kolor']
        start_szlaku_id = request.POST['start_szlaku']
        koniec_szlaku_id = request.POST['koniec_szlaku']
        
        if 'gpx_file' in request.FILES:
            gpx_file = request.FILES['gpx_file']
            gpx = gpxpy.parse(gpx_file)
            
            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        points.append((
                            point.longitude,
                            point.latitude,
                            point.elevation or 0
                        ))
            
            szlak.przebieg = LineString(points, srid=4326)
        
        szlak.kolor = kolor
        szlak.start_szlaku_id = start_szlaku_id
        szlak.koniec_szlaku_id = koniec_szlaku_id
        szlak.save()
        
        messages.success(request, f'Szlak {szlak_id} został zaktualizowany!')
        return redirect('mapa')
    
    wezly = Wezel.objects.select_related('id_obiektu').all()
    wezly_json = json.dumps([
        {
            'id': w.id,
            'nazwa': w.id_obiektu.nazwa_obiektu if w.id_obiektu else f'Węzeł {w.id}'
        }
        for w in wezly
    ], cls=DjangoJSONEncoder)
    
    return render(request, 'mapa/edytuj_szlak.html', {
        'szlak': szlak,
        'wezly': wezly,
        'wezly_json': wezly_json
    })