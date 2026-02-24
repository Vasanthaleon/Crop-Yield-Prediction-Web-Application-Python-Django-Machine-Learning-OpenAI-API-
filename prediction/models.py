from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    crop = models.CharField(max_length=100)
    season = models.CharField(max_length=50)
    area = models.FloatField()
    temperature = models.FloatField()
    rainfall = models.FloatField()
    soil_ph = models.FloatField()
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    predicted_yield = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
