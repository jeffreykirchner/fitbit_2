'''
parameterset zone minutes 
'''

from django.db import models

from main.models import ParameterSet

import main

class ParameterSetZoneMinutes(models.Model):
    '''
    parameterset zone minutes 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_zone_minutes")

    zone_minutes = models.IntegerField(verbose_name='Max Zone Minutes', default=1440)              #if <= this amount then in this bucket
    label = models.CharField(verbose_name='Label Shown', max_length = 20, default="min to min")    #label shown on display

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Zone Minutes'
        verbose_name_plural = 'Parameter Set Zone Minutes'
        ordering=['zone_minutes']
        constraints = [            
            models.UniqueConstraint(fields=['zone_minutes', 'parameter_set'], name='unique_parameter_set_zone_minutes'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.zone_minutes = source.get("zone_minutes")
        self.label = source.get("label")

        self.save()
        
        message = "Parameters loaded successfully."

        return message

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "zone_minutes" : self.zone_minutes,
            "label" : self.label,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "zone_minutes" : self.zone_minutes,
            "label" : self.label,

        }


