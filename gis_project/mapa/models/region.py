from django.contrib.gis.db import models

class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nazwa = models.CharField(max_length=100)
    lokalizacja = models.PolygonField(srid=4326)

    class Meta:
        managed = False
        db_table = 'regiony'

    def __str__(self):
        return self.nazwa

