'''
parameterset period 
'''
from tinymce.models import HTMLField

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

    show_notice = models.BooleanField(default=False, verbose_name="Show Notice")
    notice_text = HTMLField(default="Notice Text Here", verbose_name="Notice Text", blank=True)

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Period'
        verbose_name_plural = 'Parameter Set Periods'
        ordering=['period_number']
        constraints = [            
            models.UniqueConstraint(fields=['period_number', 'parameter_set'], name='unique_parameter_set_period'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset period
        '''

        self.id_label = source.get("period_number")
        self.survey_required = source.get("survey_required")
        self.survey_link = source.get("survey_link")
        self.period_type = source.get("period_type")
        self.show_notice = source.get("show_notice")
        self.notice_text = source.get("notice_text")

        self.save()
        
        message = "Parameters loaded successfully."

        return message
    
    def setup(self):
        '''
        setup period
        '''

        #add missing period payments
        for z in self.parameter_set.parameter_set_zone_minutes.all():
            obj, created = main.models.ParameterSetPeriodPayment.objects.get_or_create(parameter_set_period=self, parameter_set_zone_minutes=z)

    def copy_forward(self, source):
        '''
        copy another period into this one using copy forward function
        source : ParameterSetPeriod
        '''

        self.period_type = source.period_type

        for p_source in source.parameter_set_period_pays_a.all():
            p_target = self.parameter_set_period_pays_a.get(parameter_set_zone_minutes=p_source.parameter_set_zone_minutes)
            p_target.from_dict(p_source.json())

        self.save()

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
            "show_notice" : 1 if self.show_notice else 0,
            "notice_text" : self.notice_text,
            "parameter_set_period_payments" : [p.json() for p in self.parameter_set_period_pays_a.all()],
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
            "show_notice" : self.show_notice,
            "notice_text" : self.notice_text,
        }


