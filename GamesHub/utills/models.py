from django.db import models

class Constants(models.Model):
    variable   = models.CharField(max_length=32)
    value      = models.CharField(max_length=64)

    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

    def __str__(self):
        return self.variable
    
