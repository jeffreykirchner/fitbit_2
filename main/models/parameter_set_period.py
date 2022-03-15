'''
parameterset period 
'''

from django.db import models

from main.models import ParameterSet

from main.globals import PeriodType

import main

class ParameterSetPeriod(models.Model):
    '''
    session period parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_periods")

    period_number = models.IntegerField(verbose_name='Period Number', default=1)      #period number 1 to N
    period_type = models.CharField(max_length=100, choices=PeriodType.choices, default=PeriodType.NO_PAY) 

    survey_required = models.BooleanField(default=False, verbose_name="Survey Complete")
    survey_link = models.CharField(max_length = 1000, default = '', verbose_name = 'Survey Link')

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering=['period_number']
        constraints = [            
            models.UniqueConstraint(fields=['period_number', 'parameter_set'], name='unique_parameter_set_period'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.id_label = source.get("period_number")
        self.survey_required = source.get("survey_required")
        self.survey_link = source.get("survey_link")
        self.period_type = source.get("period_type")

        self.save()
        
        message = "Parameters loaded successfully."

        return message

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "period_number" : self.period_number,
            "survey_required" : 1 if self.survey_required else 0,
            "survey_link" : self.survey_link,
            "period_type" : self.period_type,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "period_number" : self.period_number,
            "survey_required" : self.survey_required,
            "survey_link" : self.survey_link,
            "period_type" : self.period_type,
        }


