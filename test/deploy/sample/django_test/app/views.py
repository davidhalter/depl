from django.shortcuts import render_to_response
from django.conf import settings

from . import models


def index(request):
    return render_to_response('index.html', {})


def db_add(request):
    new = models.Car(brand='Ai caramba', price=23)
    new.save()
    return render_to_response('content.html', {'content': 'saved'})


def db_show(request):
    cars = models.Car.objects.all()
    number = len(cars)
    cars.delete()
    engine = settings.DATABASES['default']['ENGINE']
    context = {'content': '%s: %s' %(engine, number)}
    return render_to_response('content.html', context)
