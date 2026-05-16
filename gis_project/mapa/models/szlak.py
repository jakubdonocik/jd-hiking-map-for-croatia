from django.contrib.gis.db import models

class Szlak(models.Model):
    id = models.AutoField(primary_key=True)
    kolor = models.CharField(max_length=20)
    start_szlaku = models.ForeignKey('Wezel', on_delete=models.CASCADE, related_name='szlaki_start', db_column='start_szlaku')
    koniec_szlaku = models.ForeignKey('Wezel', on_delete=models.CASCADE, related_name='szlaki_koniec', db_column='koniec_szlaku')
    przebieg = models.LineStringField(srid=4326)
    suma_podejsc = models.IntegerField(null=True, blank=True)
    suma_zejs = models.IntegerField(null=True, blank=True)
    dlugosc = models.IntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'szlaki'
    
    def __str__(self):
        return f"Szlak {self.id} ({self.kolor})"