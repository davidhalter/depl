from django.shortcuts import render_to_response

from . import models


def index(request):
    return render_to_response('index.html', {})


def db(request):
    new = models.Car(brand='Ai caramba', price=23)
    new.save()
    return render_to_response('index.html', {})
