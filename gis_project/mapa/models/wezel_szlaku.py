from django.db import models
from .wezel import Wezel
from .szlak import Szlak

class WezelSzlaku(models.Model):
    id = models.AutoField(primary_key=True)

    id_wezla_1 = models.ForeignKey(
        Wezel,
        on_delete=models.DO_NOTHING,
        db_column='id_wezla_1',
        related_name='wezel_start'
    )

    id_wezla_2 = models.ForeignKey(
        Wezel,
        on_delete=models.DO_NOTHING,
        db_column='id_wezla_2',
        related_name='wezel_koniec'
    )

    id_szlaku = models.ForeignKey(
        Szlak,
        on_delete=models.DO_NOTHING,
        db_column='id_szlaku'
    )

    class Meta:
        managed = False
        db_table = 'wezly_szlaku'
