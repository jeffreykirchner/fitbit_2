'''
parameterset period 
'''
from tinymce.models import HTMLField

from django.db import models

from main.models import ParameterSet

from main.globals import PeriodType
from main.globals import format_minutes

import main

class ParameterSetPeriod(models.Model):
    '''
    session period parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_periods")
    parameter_set_pay_block = models.ForeignKey('main.ParameterSetPayBlock', on_delete=models.CASCADE, related_name="parameter_set_periods_b", blank=True, null=True)

    period_number = models.IntegerField(verbose_name='Period Number', default=1)                                       #period number 1 to N
    period_type = models.CharField(max_length=100, choices=PeriodType.choices, default=PeriodType.NO_PAY)              #type of payment system used

    survey_required = models.BooleanField(default=False, verbose_name="Survey Required")                               #if true show the survey below
    survey_link = models.CharField(max_length = 1000, default = 'https://www.google.com', verbose_name = 'Survey Link', blank=True)

    show_notice = models.BooleanField(default=False, verbose_name="Show Notice")                                       #if true show notice below
    notice_text = HTMLField(default="Notice Text Here", verbose_name="Notice Text", blank=True)

    minimum_wrist_minutes = models.IntegerField(default = 1080)                                                        #minimum wrist time to get paid today

    show_graph_1 = models.BooleanField(default=False, verbose_name="Show Graph 1")                                       #if true show the graph
    graph_1_start_period_number = models.IntegerField(verbose_name='Graph 1 Start Period', default=1)                    #period number to start the graph on
    graph_1_end_period_number = models.IntegerField(verbose_name='Graph 1 End Period', default=1)                        #period number to end the graph on
    
    show_graph_2 = models.BooleanField(default=False, verbose_name="Show Graph 2")                                       #if true show the graph
    graph_2_start_period_number = models.IntegerField(verbose_name='Graph 2 Start Period', default=1)                    #period number to start the graph on
    graph_2_end_period_number = models.IntegerField(verbose_name='Graph 2 End Period', default=1)                        #period number to end the graph on

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"Period {self.period_number}"

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
        self.minimum_wrist_minutes = source.get("minimum_wrist_minutes")

        self.show_graph_1 = source.get("show_graph_1")
        self.graph_1_start_period_number = source.get("graph_1_start_period_number")
        self.graph_1_end_period_number = source.get("graph_1_end_period_number")

        self.show_graph_2 = source.get("show_graph_2")
        self.graph_2_start_period_number = source.get("graph_2_start_period_number")
        self.graph_2_end_period_number = source.get("graph_2_end_period_number")

        self.pay_block = source.get("pay_block")

        parameter_set_pay_block_source = source.get("parameter_set_pay_block")
        if parameter_set_pay_block_source['id'] != -1:
            self.parameter_set_pay_block = self.parameter_set.parameter_set_pay_blocks_a.get(pay_block_number=parameter_set_pay_block_source['pay_block_number'])

        self.save()

        new_parameter_set_period_payments = source.get("parameter_set_period_payments")
        new_parameter_set_period_payments_order = source.get("parameter_set_period_payments_order")
        for index, p in enumerate(self.parameter_set_period_pays_a.all()):   
            temp_id = new_parameter_set_period_payments_order[index]
            temp_v = new_parameter_set_period_payments[str(temp_id)]
            p.from_dict(temp_v)

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
        self.minimum_wrist_minutes = source.minimum_wrist_minutes
        self.show_graph_1 = source.show_graph_1
        self.graph_1_start_period_number = source.graph_1_start_period_number
        self.graph_1_end_period_number = source.graph_1_end_period_number
        self.show_graph_2 = source.show_graph_2
        self.graph_2_start_period_number = source.graph_2_start_period_number
        self.graph_2_end_period_number = source.graph_2_end_period_number
        self.parameter_set_pay_block = source.parameter_set_pay_block

        for p_source in source.parameter_set_period_pays_a.all():
            p_target = self.parameter_set_period_pays_a.get(parameter_set_zone_minutes=p_source.parameter_set_zone_minutes)
            p_target.from_dict(p_source.json())

        self.save()

    def get_payment(self, minutes):
        '''
        return payment given minutes
        '''

        for p in self.parameter_set_period_pays_a.all():
            if minutes <= p.parameter_set_zone_minutes.zone_minutes:
                return p

        return None

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
            "minimum_wrist_minutes" : self.minimum_wrist_minutes,
            "minimum_wrist_minutes_str" : format_minutes(self.minimum_wrist_minutes),
            "show_notice" : 1 if self.show_notice else 0,
            "notice_text" : self.notice_text,

            "show_graph_1" : 1 if self.show_graph_1 else 0,
            "graph_1_start_period_number" : self.graph_1_start_period_number,
            "graph_1_end_period_number" : self.graph_1_end_period_number,

            "show_graph_2" : 1 if self.show_graph_2 else 0,
            "graph_2_start_period_number" : self.graph_2_start_period_number,
            "graph_2_end_period_number" : self.graph_2_end_period_number,

            "parameter_set_pay_block" : self.parameter_set_pay_block.json_for_parameter_set() if self.parameter_set_pay_block else {'id' : -1},

            "parameter_set_period_payments" : {p.id : p.json() for p in self.parameter_set_period_pays_a.all()},
            "parameter_set_period_payments_order" : list(self.parameter_set_period_pays_a.all().values_list('id', flat=True))
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
            "minimum_wrist_minutes" : self.minimum_wrist_minutes,
            "minimum_wrist_minutes_str" : format_minutes(self.minimum_wrist_minutes),
            "show_notice" : self.show_notice,
            "notice_text" : self.notice_text,

            "show_graph_1" : 1 if self.show_graph_1 else 0,
            "graph_1_start_period_number" : self.graph_1_start_period_number,
            "graph_1_end_period_number" : self.graph_1_end_period_number,

            "show_graph_2" : 1 if self.show_graph_2 else 0,
            "graph_2_start_period_number" : self.graph_2_start_period_number,
            "graph_2_end_period_number" : self.graph_2_end_period_number,

            "parameter_set_pay_block" : self.parameter_set_pay_block.json_for_parameter_set() if self.parameter_set_pay_block else {'id' : -1},

            "parameter_set_period_payments" : [p.json() for p in self.parameter_set_period_pays_a.all()],
        }


