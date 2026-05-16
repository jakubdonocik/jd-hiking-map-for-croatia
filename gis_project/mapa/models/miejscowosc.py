from django.contrib.gis.db import models
from .region import Region

class Miejscowosc(models.Model):
    id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.DO_NOTHING,
        db_column='region'
    )
    lokalizacja = models.PolygonField(srid=4326)

    class Meta:
        managed = False
        db_table = 'miejscowosci'

    def __str__(self):
        return self.nazwa
