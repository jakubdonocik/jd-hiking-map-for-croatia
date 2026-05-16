from django.db import models
from .obiekt import Obiekt

class Wezel(models.Model):
    id = models.AutoField(primary_key=True)

    id_obiektu = models.ForeignKey(
        Obiekt,
        on_delete=models.DO_NOTHING,
        db_column='id_obiektu'
    )

    class Meta:
        managed = False
        db_table = 'wezly'

    def __str__(self):
        return f"Wezel {self.id} ({self.id_obiektu})"
