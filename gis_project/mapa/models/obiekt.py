from django.contrib.gis.db import models
from .rodzaj_obiektu import RodzajObiektu
from .miejscowosc import Miejscowosc
from .region import Region

class Obiekt(models.Model):
    id = models.AutoField(primary_key=True)
    nazwa_obiektu = models.CharField(max_length=100)

    rodzaj_obiektu = models.ForeignKey(
        RodzajObiektu,
        on_delete=models.DO_NOTHING,
        db_column='rodzaj_obiektu'
    )

    miejscowosc = models.ForeignKey(
        Miejscowosc,
        on_delete=models.DO_NOTHING,
        db_column='miejscowosc'
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.DO_NOTHING,
        db_column='region'
    )

    opis = models.TextField(null=True, blank=True)
    lokalizacja = models.PointField(srid=4326)

    class Meta:
        managed = False
        db_table = 'obiekty'

    def __str__(self):
        return self.nazwa_obiektu
