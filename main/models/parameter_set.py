'''
parameter set
'''
import logging

from tinymce.models import HTMLField

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError
from django.core.serializers.json import DjangoJSONEncoder

from main.globals import get_random_hex_color
from main.globals import ColorAssignmentType

from main.models import InstructionSet
from main.models import HelpDocSubjectSet

import main

#experiment session parameters
class ParameterSet(models.Model):
    '''
    parameter set
    '''    
    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.CASCADE, related_name="parameter_sets")
    help_doc_subject_set = models.ForeignKey(HelpDocSubjectSet, on_delete=models.CASCADE, related_name="parameter_sets_b", null=True)
    
    enable_chat = models.BooleanField(default=False, verbose_name = 'Enable Chat')                           #if true subjects can privately chat one on one
    show_instructions = models.BooleanField(default=False, verbose_name = 'Show Instructions')                #if true show instructions
    show_history = models.BooleanField(default=False, verbose_name = 'Show History')                          #if true show history

    graph_y_max = models.IntegerField(verbose_name='Graph: Y Max', default=75)           #max height of subject graph
    group_size = models.IntegerField(verbose_name='Group Size', default=2)               #max height of subject graph
    color_assignment_type = models.CharField(max_length=100, choices=ColorAssignmentType.choices, default=ColorAssignmentType.FIXED, verbose_name='Color Assignment Type')  #how player colors are assigned

    test_mode = models.BooleanField(default=False, verbose_name = 'Test Mode')                                #if true subject screens will do random auto testing

    consent_form = models.CharField(verbose_name='Consent Form File Name', max_length = 100, default="file_name.pdf")    #consent for file name
    consent_form_required = models.BooleanField(default=False, verbose_name = 'Consent Form Required')                   #consent form required

    partner_string = models.CharField(verbose_name='Partner String', max_length = 200, default="", blank=True)             #partner string field

    completion_message = HTMLField(default="The study is complete, thank you for your participation.", verbose_name="End of study message", blank=True)

    age_warning = models.IntegerField(verbose_name='Age Warning', default=25)                     #age cut off that issues a warning for invalid age range
    reconnection_limit = models.IntegerField(verbose_name='Reconnection Limit', default=10)       #number of times a subject can reconnect before they are blocked from reconnecting again

    json_for_session_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)                   #json model of parameter set 
    json_for_subject_json = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)                   #json model of parameter set for subject

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.enable_chat = True if new_ps.get("enable_chat") == "True" else False
            self.show_instructions = True if new_ps.get("show_instructions") == "True" else False
            self.show_history = True if new_ps.get("show_history") == "True" else False
            self.graph_y_max = new_ps.get("graph_y_max")
            self.group_size = new_ps.get("group_size")
            self.color_assignment_type = new_ps.get("color_assignment_type")
            self.age_warning = new_ps.get("age_warning")
            self.reconnection_limit = new_ps.get("reconnection_limit")

            self.consent_form = new_ps.get("consent_form")
            self.consent_form_required = True if new_ps.get("consent_form_required") == "True" else False
            self.partner_string = new_ps.get("partner_string", "")

            self.completion_message = new_ps.get("completion_message")

            self.save()

            instruction_sets = InstructionSet.objects.filter(label=new_ps.get("instruction_set")["label"])

            if instruction_sets:
                self.instruction_set = instruction_sets.first()

            help_doc_subject_sets = HelpDocSubjectSet.objects.filter(label=new_ps.get("help_doc_subject_set")["label"])
            if help_doc_subject_sets:
                self.help_doc_subject_set = help_doc_subject_sets.first()

            self.save()

            #players
            new_parameter_set_players = new_ps.get("parameter_set_players")
            
            self.parameter_set_players.all().delete()

            new_parameter_set_players = new_ps.get("parameter_set_players")
            for p in new_parameter_set_players:    
                new_player = self.add_new_player()            
                new_player.from_dict(new_parameter_set_players[p])

            #pay blocks
            new_parameter_set_pay_blocks = new_ps.get("parameter_set_pay_blocks", None)

            self.parameter_set_pay_blocks_a.all().delete()

            for p in new_parameter_set_pay_blocks:      
                payblock = self.add_new_pay_block()          
                payblock.from_dict(new_parameter_set_pay_blocks[p])

            #periods
            new_parameter_set_periods = new_ps.get("parameter_set_periods")
            self.parameter_set_periods.all().delete()

            for p in new_parameter_set_periods:    
                new_period = self.add_new_period()           
                new_period.from_dict(new_parameter_set_periods[p])

            self.json(update_required=True)

        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    

        if self.parameter_set_periods.count() == 0:
           self.add_new_period()
        
        if self.parameter_set_players.count() == 0:
            self.add_new_player()
        
        if self.parameter_set_pay_blocks_a.count() == 0:
            self.add_new_pay_block()

    def add_new_player(self):
        '''
        add a new player of type subject_type
        '''

        player = main.models.ParameterSetPlayer()
        player.parameter_set = self
        # player.id_label = self.parameter_set_players.count() + 1
        # player.display_color = get_random_hex_color()

        v = main.globals.get_color_by_group(self.group_size, self.parameter_set_players.count() + 1)

        player.id_label = v["label"]
        player.display_color = v["color"]

        player.save()

        return player
    
    def add_new_period(self):
        '''
        add new parameter set period
        '''

        parameter_set_period = main.models.ParameterSetPeriod()

        parameter_set_period.parameter_set = self

        if self.parameter_set_periods.count() == 0:
            parameter_set_period.period_number = 1
        else:
            parameter_set_period.period_number = self.parameter_set_periods.last().period_number+1

        parameter_set_period.save()
        parameter_set_period.setup()

        return parameter_set_period
    
    def add_new_pay_block(self):
        '''
        add new pay block
        '''

        pay_block_last = self.parameter_set_pay_blocks_a.all().last()

        new_pay_block = main.models.ParameterSetPayBlock()
        new_pay_block.parameter_set = self
        new_pay_block.pay_block_number = pay_block_last.pay_block_number + 1 if pay_block_last else 1

        new_pay_block.save()

        return new_pay_block

    def update_json_local(self):
        '''
        update json model
        '''

        self.json_for_session_json["id"] = self.id     

        self.json_for_session_json["enable_chat"] = "True" if self.enable_chat else "False"
        self.json_for_session_json["show_instructions"] = "True" if self.show_instructions else "False"
        self.json_for_session_json["show_history"] = "True" if self.show_history else "False"
        self.json_for_session_json["instruction_set"] = self.instruction_set.json_min()
        self.json_for_session_json["graph_y_max"] = self.graph_y_max
        self.json_for_session_json["group_size"] = self.group_size
        self.json_for_session_json["color_assignment_type"] = self.color_assignment_type
        self.json_for_session_json["age_warning"] = self.age_warning
        self.json_for_session_json["reconnection_limit"] = self.reconnection_limit

        self.json_for_session_json["consent_form"] = self.consent_form
        self.json_for_session_json["consent_form_required"] = "True" if self.consent_form_required else "False"
        self.json_for_session_json["partner_string"] = self.partner_string

        self.json_for_session_json["completion_message"] = self.completion_message

        self.json_for_session_json["help_doc_subject_set"] =  self.help_doc_subject_set.json() if self.help_doc_subject_set else {"id":None}

        self.json_for_session_json["test_mode"] = "True" if self.test_mode else "False"

        self.save()
    
    def update_json_fk(self, update_players=False, update_periods=False, update_pay_blocks=False):
        '''
        update json model
        '''

        if update_players:
            self.json_for_session_json["parameter_set_players"] = {str(p.id) : p.json() for p in self.parameter_set_players.all()}
            self.json_for_session_json["parameter_set_players_order"] = list(self.parameter_set_players.all().values_list('id', flat=True))

        if update_periods:
            self.json_for_session_json["parameter_set_periods"] = {str(p.id) : p.json() for p in self.parameter_set_periods.all().prefetch_related()}
            self.json_for_session_json["parameter_set_periods_order"] = list(self.parameter_set_periods.all().values_list('id', flat=True))

        if update_pay_blocks:
            self.json_for_session_json["parameter_set_pay_blocks"] = {str(p.id) : p.json() for p in self.parameter_set_pay_blocks_a.all()}
            self.json_for_session_json["parameter_set_pay_blocks_order"] = list(self.parameter_set_pay_blocks_a.all().values_list('id', flat=True))

        self.save()

    def json(self, update_required=False):
        '''
        return json object of model
        '''
        if not self.json_for_session_json or \
           update_required:
            self.json_for_session_json = {}
            self.update_json_local()
            self.update_json_fk(update_players=True, update_periods=True,  update_pay_blocks=True)

        return self.json_for_session_json
    
    def json_for_subject(self, update_required=False):
        '''
        return json object for subject
        '''
        if update_required or not self.json_for_subject_json:

            self.json_for_subject_json = {
                "id" : self.id,
                
                "show_instructions" : "True" if self.show_instructions else "False",
                "test_mode" : self.test_mode,
                "graph_y_max" : self.graph_y_max,
                "consent_form" : self.consent_form,
                "consent_form_required" : self.consent_form_required,
                "parameter_set_pay_blocks" : {p.id : p.json() for p in self.parameter_set_pay_blocks_a.all()},
                "parameter_set_pay_blocks_order" : list(self.parameter_set_pay_blocks_a.all().values_list('id', flat=True)),
                "completion_message" : self.completion_message,
                "partner_string" : self.partner_string,
                "reconnection_limit" : self.reconnection_limit,
            }

            self.save()

        return self.json_for_subject_json


