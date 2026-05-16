from django.db import models
from django.contrib.auth.models import User
from .obiekt import Obiekt

class MiejscaUzytkownika(models.Model):
    id = models.AutoField(primary_key=True)

    id_uzytkownika = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='id_uzytkownika'
    )

    id_obiektu = models.ForeignKey(
        Obiekt,
        on_delete=models.DO_NOTHING,
        db_column='id_obiektu'
    )

    data_dodania = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'miejsca_uzytkownika'
