from django.db import models

# Create your models here.

class Car(models.Model):
    brand = models.TextField()
    price = models.FloatField()
