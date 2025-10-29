from django.db import models

class Constants(models.Model):
    variable   = models.CharField(max_length=32)
    value      = models.IntegerField()

    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value