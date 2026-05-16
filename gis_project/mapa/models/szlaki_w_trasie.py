from django.db import models
from .szlak import Szlak
from .ulubione_trasy import UlubioneTrasy

class SzlakiWTrasie(models.Model):
    id = models.AutoField(primary_key=True)

    kolejnosc = models.IntegerField()

    id_szlaku = models.ForeignKey(
        Szlak,
        on_delete=models.DO_NOTHING,
        db_column='id_szlaku'
    )

    id_trasy = models.ForeignKey(
        UlubioneTrasy,
        on_delete=models.DO_NOTHING,
        db_column='id_trasy'
    )

    class Meta:
        managed = False
        db_table = 'szlaki_w_trasie'
