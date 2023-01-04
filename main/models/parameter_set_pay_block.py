'''
parameterset pay block 
'''
from tinymce.models import HTMLField

from django.db import models

from main.models import ParameterSet

from main.globals import PayBlockType
from main.globals import format_minutes

import main

class ParameterSetPayBlock(models.Model):
    '''
    parameters set pay block 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_pay_blocks_a")

    pay_block_type = models.CharField(max_length=100, choices=PayBlockType.choices, default=PayBlockType.NO_PAY)          #type of payment system used
    pay_block_number = models.IntegerField(verbose_name='Pay Block Number', default=1)                                           #group period together with the same group to be paid together

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"Period {self.period_number}"

    class Meta:
        verbose_name = 'Parameter Set Pay Block'
        verbose_name_plural = 'Parameter Set Pay Blocks'
        ordering=['pay_block_number']
        constraints = [            
            models.UniqueConstraint(fields=['pay_block_number', 'parameter_set'], name='unique_parameter_set_pay_block'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset period
        '''

        self.pay_block_type = source.get("pay_block_type")
        self.pay_block_number = source.get("pay_block_number")
        

        self.save()

        new_parameter_set_block_payments = source.get("parameter_set_block_payments")
        for index, p in enumerate(self.parameter_set_block_payments_a.all()):                
                p.from_dict(new_parameter_set_block_payments[index])

        message = "Parameters loaded successfully."

        return message
    
    def setup(self):
        '''
        setup period
        '''

        #add missing period payments
        for z in self.parameter_set.parameter_set_zone_minutes.all():
            obj, created = main.models.ParameterSetPayBlockPayment.objects.get_or_create(parameter_set_period=self, parameter_set_zone_minutes=z)

    def get_payment(self, minutes):
        '''
        return payment given minutes
        '''

        # for p in self.parameter_set_period_pays_a.all():
        #     if minutes <= p.parameter_set_zone_minutes.zone_minutes:
        #         return p

        return None

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "pay_block_type" : self.pay_block_type,
            "pay_block_number" : self.pay_block_number,

            "parameter_set_pay_block_payments" : [p.json() for p in self.parameter_set_pay_block_payments_a.all()],
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,

            "id" : self.id,
            "pay_block_type" : self.pay_block_type,
            "pay_block_number" : self.pay_block_number,

            "parameter_set_pay_block_payments" : [p.json() for p in self.parameter_set_pay_block_payments_a.all()],
        }


