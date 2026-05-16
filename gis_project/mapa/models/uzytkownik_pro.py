from django.db import models
from django.contrib.auth.models import User

class UzytkownikPro(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil_pro',
        null=True,
        blank=True
    )
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    haslo = models.CharField(max_length=150)  
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'uzytkownicy_pro'
    
    def __str__(self):
        return f"{self.imie} {self.nazwisko}"