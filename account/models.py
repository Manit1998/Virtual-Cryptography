from django.db import models
from django.utils import timezone


class data(models.Model):
    share_name = models.CharField(max_length=200)
    def __str__(self):             
        return self.share_name