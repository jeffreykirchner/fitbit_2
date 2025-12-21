'''
parameterset pay block 
'''
from tinymce.models import HTMLField

from django.db import models

from main.models import ParameterSet

from main.globals import PayBlockType
from main.globals import format_minutes
from main.globals import GroupAssignmentType

import main

class ParameterSetPayBlock(models.Model):
    '''
    parameters set pay block 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_pay_blocks_a")

    pay_block_type = models.CharField(max_length=100, choices=PayBlockType.choices, default=PayBlockType.FIXED_PAY_ONLY)         #type of payment system used
    pay_block_number = models.IntegerField(verbose_name='Pay Block Number', default=1)                                           #ordering index of payblocks

    fixed_pay = models.DecimalField(verbose_name='Individual Payment', decimal_places=2, default=0, max_digits=5)
    no_pay_percent = models.IntegerField(verbose_name='No Pay Fitbit Percent', default=0)
    group_assignment_type = models.CharField(max_length=100, choices=GroupAssignmentType.choices, default=GroupAssignmentType.FIXED) #how groups are assigned each period block

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"Pay Block {self.pay_block_number}"

    class Meta:
        verbose_name = 'Parameter Set Pay Block'
        verbose_name_plural = 'Parameter Set Pay Blocks'
        ordering=['pay_block_number']
        constraints = [            
            models.UniqueConstraint(fields=['pay_block_number', 'parameter_set'], name='unique_parameter_set_pay_block'),
        ]

    def from_dict(self, source, update_block_number=True):
        '''
        copy source values into this period
        source : dict object of parameterset period
        '''

        self.pay_block_type = source.get("pay_block_type")
        self.fixed_pay = source.get("fixed_pay")
        self.no_pay_percent = source.get("no_pay_percent")

        if update_block_number:
            self.pay_block_number = source.get("pay_block_number")
        
        self.save()

        new_parameter_set_block_payments = source.get("parameter_set_pay_block_payments")
        new_parameter_set_block_payments_order = source.get("parameter_set_pay_block_payments_order")

        self.parameter_set_pay_block_payments_a.all().delete()

        if len(new_parameter_set_block_payments_order) > 0:
            for p in new_parameter_set_block_payments:      
                new_payblock_payment = self.add_pay_block_payment()       
                new_payblock_payment.from_dict(new_parameter_set_block_payments[p])

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

        for p in self.parameter_set_pay_block_payments_a.all():
            if minutes <= p.zone_minutes:
                return p

        return None
    
    def add_pay_block_payment(self):
        '''
        add a new pay bock payment
        '''
        first_bock_payment = self.parameter_set_pay_block_payments_a.first()

        block_payment = main.models.ParameterSetPayBlockPayment()
        block_payment.parameter_set_pay_block = self

        if first_bock_payment:
            block_payment.zone_minutes = first_bock_payment.zone_minutes - 1

        block_payment.save()

        return block_payment

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "pay_block_type" : self.pay_block_type,
            "pay_block_number" : self.pay_block_number,

            "fixed_pay" : round(self.fixed_pay,2),
            "no_pay_percent" : self.no_pay_percent,
            "group_assignment_type" : self.group_assignment_type,

            "parameter_set_pay_block_payments" : {p.id : p.json() for p in self.parameter_set_pay_block_payments_a.all()},
            "parameter_set_pay_block_payments_order" : list(self.parameter_set_pay_block_payments_a.all().values_list('id', flat=True)),
        }
    
    def json_for_parameter_set(self):
        return{

            "id" : self.id,
            "pay_block_number" : self.pay_block_number,
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

            "fixed_pay" : round(self.fixed_pay),
            "no_pay_percent" : self.no_pay_percent,            

            "parameter_set_pay_block_payments" : [p.json() for p in self.parameter_set_pay_block_payments_a.all()],
        }


