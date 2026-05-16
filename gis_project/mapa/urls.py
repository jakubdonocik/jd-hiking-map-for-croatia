from django.urls import path
from .views import mapa_view, regiony_geojson
from . import views
from .views import dodaj_obiekt
from .views import wyznacz_trase

urlpatterns = [
    path('', mapa_view, name='mapa'),
    path('regiony_geojson/', regiony_geojson),
    path('api/obiekty/', views.obiekty_geojson),
    path('api/szlaki/', views.szlaki_geojson),
    path('dodaj-szlak/', views.dodaj_szlak, name='dodaj_szlak'),
    path('dodaj-obiekt/', dodaj_obiekt, name='dodaj_obiekt'),
    path('edytuj-obiekt/<int:obiekt_id>/', views.edytuj_obiekt, name='edytuj_obiekt'),
    path('api/wezly/', views.wezly_geojson),
    path('lista-szlakow/', views.lista_szlakow, name='lista_szlakow'),
    path('usun-szlak/<int:szlak_id>/', views.usun_szlak, name='usun_szlak'),
    path('api/szlaki-lista/', views.szlaki_lista_json, name='szlaki_lista_json'),
    path('api/obiekty-lista/', views.obiekty_lista_json, name='obiekty_lista_json'),
    path('usun-obiekt/<int:obiekt_id>/', views.usun_obiekt, name='usun_obiekt'),
    path('api/pobierz-wysokosc/', views.pobierz_wysokosc, name='pobierz_wysokosc'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/wyznacz-trase/', wyznacz_trase),
    path('api/graf-wezlow/', views.graf_wezlow, name='graf_wezlow'),
    path('edytuj-szlak/<int:szlak_id>/', views.edytuj_szlak, name='edytuj_szlak'),
]