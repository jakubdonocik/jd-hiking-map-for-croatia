from django.db import models
from .obiekt import Obiekt
from django.contrib.auth.models import User

class UlubioneMiejsca(models.Model):
    id = models.AutoField(primary_key=True)

    nazwa_obiektu = models.CharField(max_length=100)

    id_obiektu = models.ForeignKey(
        Obiekt,
        on_delete=models.DO_NOTHING,
        db_column='id_obiektu'
    )

    id_uzytkownika = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='id_uzytkownika'
    )

    class Meta:
        managed = False
        db_table = 'ulubione_miejsca'
