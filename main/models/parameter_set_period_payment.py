'''
parameterset period payments
'''

from django.db import models

from main.models import ParameterSetPeriod

from main.globals import PeriodType

import main

class ParameterSetPeriodPayment(models.Model):
    '''
    session period payment parameters 
    '''

    parameter_set_period = models.ForeignKey(ParameterSetPeriod, on_delete=models.CASCADE, related_name="parameter_set_period_individual_pays_a")
    parameter_set_zone_minutes = models.ForeignKey('main.ParameterSetZoneMinutes', on_delete=models.CASCADE, related_name="parameter_set_period_individual_pays_b")

    payment = models.DecimalField(decimal_places=2, default=0, max_digits=5)            #amount individual earns reaching this activity level
    group_bonus = models.DecimalField(decimal_places=2, default=0, max_digits=5)        #amount group earns if reaching this acttvity level

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Period Pay'
        verbose_name_plural = 'Parameter Set Payments'
        constraints = [            
            models.UniqueConstraint(fields=['parameter_set_period', 'parameter_set_zone_minutes'], name='unique_parameter_set_payments'),
        ]
        ordering=['parameter_set_zone_minutes__zone_minutes']

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset period individual pay
        '''

        self.payment = source.get("payment")
        self.group_bonus = source.get("group_bonus")

        self.save()
        
        message = "Parameters loaded successfully."

        return message

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "payment" : self.payment,
            "group_bonus" : self.group_bonus,
            "parameter_set_zone_minutes" : self.parameter_set_zone_minutes.json(),
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "payment" : self.payment,
            "group_bonus" : self.group_bonus,
        }


