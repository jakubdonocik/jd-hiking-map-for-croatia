from django.db import models
from .szlak import Szlak
from django.contrib.auth.models import User

class UlubioneTrasy(models.Model):
    id = models.AutoField(primary_key=True)

    id_trasy = models.ForeignKey(
        Szlak,
        on_delete=models.DO_NOTHING,
        db_column='id_trasy'
    )

    nazwa = models.CharField(max_length=100)
    data_utworzenia = models.DateTimeField()

    id_uzytkownika = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='id_uzytkownika'
    )

    class Meta:
        managed = False
        db_table = 'ulubione_trasy'
