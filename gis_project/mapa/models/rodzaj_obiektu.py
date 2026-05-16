from django.db import models

class RodzajObiektu(models.Model):
    id = models.AutoField(primary_key=True)
    rodzaj_obiektu = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'rodzaje_obiektow'

    def __str__(self):
        return self.rodzaj_obiektu
