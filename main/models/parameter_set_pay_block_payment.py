'''
parameterset period payments
'''

from django.db import models

from main.models import ParameterSetPayBlock


import main

class ParameterSetPayBlockPayment(models.Model):
    '''
    session period payment parameters 
    '''

    parameter_set_pay_block = models.ForeignKey(ParameterSetPayBlock, on_delete=models.CASCADE, related_name="parameter_set_pay_block_payments_a")


    zone_minutes = models.IntegerField(verbose_name='Max Zone Minutes', default=1440)                                #if <= this amount then in this bucket
    payment = models.DecimalField(verbose_name='Individual Payment', decimal_places=2, default=0, max_digits=5)      #amount individual earns reaching this activity level
    group_bonus = models.DecimalField(verbose_name='Group Payment', decimal_places=2, default=0, max_digits=5)       #amount group earns if reaching this acttvity level
    no_pay_percent = models.IntegerField(verbose_name='No Pay Fitbit Percent', default=0)                            #amount of fitbit earned by checking in today
    label = models.CharField(verbose_name='Label Shown', max_length = 20, default="min to min")                      #label shown on display

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Pay Block Payment'
        verbose_name_plural = 'arameter Set Pay Block Payments'
        constraints = [            
            models.UniqueConstraint(fields=['parameter_set_pay_block', 'zone_minutes'], name='unique_parameter_set_pay_block_payment'),
        ]
        ordering=['zone_minutes']

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset period individual pay
        '''

        self.zone_minutes = source.get("zone_minutes")
        self.payment = source.get("payment")
        self.group_bonus = source.get("group_bonus")
        self.no_pay_percent = source.get("no_pay_percent")

        self.save()
        
        message = "Parameters loaded successfully."

        return message

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,

            "label" : self.label,
            "zone_minutes" : round(self.zone_minutes),
            "payment" : round(self.payment),
            "group_bonus" : round(self.group_bonus),
            "no_pay_percent" : self.no_pay_percent,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,

            "label" : self.label,
            "zone_minutes" : round(self.zone_minutes),
            "payment" : round(self.payment),
            "group_bonus" : self.group_bonus,
            "no_pay_percent" : self.no_pay_percent,
        }


