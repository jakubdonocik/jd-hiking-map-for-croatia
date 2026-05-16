from django.db import models
from django.contrib.gis.db import models


class RodzajObiektu(models.Model):
    nazwa = models.CharField(max_length=100)

    class Meta:
        db_table = 'rodzaje_obiektow'
        managed = False  

    def __str__(self):
        return self.nazwa


class Obiekt(models.Model):
    nazwa_obiektu = models.CharField(max_length=255)
    rodzaj_obiektu = models.ForeignKey(
        RodzajObiektu,
        on_delete=models.PROTECT,
        db_column='rodzaj_obiektu'
    )
    lokalizacja = models.PointField(srid=4326)
    miejscowosc = models.ForeignKey(
        'Miejscowosc',
        null=True,
        on_delete=models.SET_NULL
    )
    region = models.ForeignKey(
        'Region',
        null=True,
        on_delete=models.SET_NULL
    )
    opis = models.TextField(blank=True)

    class Meta:
        db_table = 'obiekty'
        managed = False


class Szlak(models.Model):
    kolor = models.CharField(max_length=20)
    przebieg = models.LineStringField(srid=4326)

    class Meta:
        db_table = 'szlaki'

