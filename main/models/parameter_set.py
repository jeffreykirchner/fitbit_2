'''
parameter set
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.globals import get_random_hex_color

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

    graph_y_max = models.IntegerField(verbose_name='Graph: Y Max', default=75)           #max height of subject graph
    group_size = models.IntegerField(verbose_name='Group Size', default=2)               #max height of subject graph

    test_mode = models.BooleanField(default=False, verbose_name = 'Test Mode')                                #if true subject screens will do random auto testing

    consent_form = models.CharField(verbose_name='Consent Form File Name', max_length = 100, default="file_name.pdf")    #consent for file name
    consent_form_required = models.BooleanField(default=False, verbose_name = 'Consent Form Required')                   #consent form required

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

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
            self.enable_chat = new_ps.get("enable_chat")
            self.show_instructions = new_ps.get("show_instructions")
            self.graph_y_max = new_ps.get("graph_y_max")
            self.group_size = new_ps.get("group_size")

            self.consent_form = new_ps.get("consent_form")
            self.consent_form_required = new_ps.get("consent_form_required")

            self.instruction_set = InstructionSet.objects.get(label=new_ps.get("instruction_set")["label"])

            if new_ps.get("help_doc_subject_set")["id"]:
                self.help_doc_subject_set = HelpDocSubjectSet.objects.get(label=new_ps.get("help_doc_subject_set")["label"])

            self.save()

            #players
            new_parameter_set_players = new_ps.get("parameter_set_players")
            
            self.parameter_set_players.all().delete()

            for i in range(len(new_parameter_set_players)):
                self.add_new_player()

            new_parameter_set_players = new_ps.get("parameter_set_players")
            for index, p in enumerate(self.parameter_set_players.all()):                
                p.from_dict(new_parameter_set_players[index])
            

            #zone minutes
            new_parameter_set_zone_minutes = new_ps.get("parameter_set_zone_minutes")

            self.parameter_set_zone_minutes.all().delete()

            for i in range(len(new_parameter_set_zone_minutes)):
                    self.add_new_zone_minutes()

            for index, p in enumerate(self.parameter_set_zone_minutes.all()):                
                p.from_dict(new_parameter_set_zone_minutes[index])

            #periods
            new_parameter_set_periods = new_ps.get("parameter_set_periods")
            self.parameter_set_periods.all().delete()

            for i in range(len(new_parameter_set_periods)):
                    self.add_new_period()

            for index, p in enumerate(self.parameter_set_periods.all()):                
                p.from_dict(new_parameter_set_periods[index])


        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        if self.parameter_set_zone_minutes.count() == 0:
            parameter_set_zone_minutes = main.models.ParameterSetZoneMinutes()
            parameter_set_zone_minutes.parameter_set = self
            parameter_set_zone_minutes.save()

        if self.parameter_set_periods.count() == 0:
            parameter_set_period = main.models.ParameterSetPeriod()
            parameter_set_period.parameter_set = self
            parameter_set_period.save()
            parameter_set_period.setup()
        
        if self.parameter_set_players.count() == 0:
            parameter_set_player = main.models.ParameterSetPlayer()
            parameter_set_player.parameter_set = self
            parameter_set_player.save()

    def add_new_player(self):
        '''
        add a new player of type subject_type
        '''

        player = main.models.ParameterSetPlayer()
        player.parameter_set = self
        player.id_label = self.parameter_set_players.count() + 1
        player.display_color = get_random_hex_color()

        player.save()
    
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
    
    def add_new_zone_minutes(self):
        '''
        add new parameter set zone minutes
        '''
        logger = logging.getLogger(__name__) 

        parameter_set_zone_minutes = main.models.ParameterSetZoneMinutes()

        new_zone_minutes = -1

        for i in range(1441):
            if self.parameter_set_zone_minutes.filter(zone_minutes=i).count() == 0:
                new_zone_minutes = i
                #logger.info(f'add_new_zone_minutes: new_zone_minutes {new_zone_minutes}')
                break

        if new_zone_minutes == -1:
            logger.warning(f'add_new_zone_minutes: no slot found for parameter set {self.id}')
            return

        parameter_set_zone_minutes.parameter_set = self
        parameter_set_zone_minutes.zone_minutes = new_zone_minutes

        parameter_set_zone_minutes.save()

        for p in self.parameter_set_periods.all():
            p.setup()

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,            

            "enable_chat" : "True" if self.enable_chat else "False",
            "show_instructions" : "True" if self.show_instructions else "False",
            "instruction_set" : self.instruction_set.json_min(),
            "graph_y_max" : self.graph_y_max,
            "group_size" : self.group_size,

            "parameter_set_players" : [p.json() for p in self.parameter_set_players.all()],
            "parameter_set_periods" : [p.json() for p in self.parameter_set_periods.all().prefetch_related()],
            "parameter_set_zone_minutes" : [p.json() for p in self.parameter_set_zone_minutes.all()],

            "consent_form" : self.consent_form,
            "consent_form_required" : "True" if self.consent_form_required else "False",

            "help_doc_subject_set" : self.help_doc_subject_set.json() if self.help_doc_subject_set else {"id":None},

            "test_mode" : "True" if self.test_mode else "False",
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,
            
            "show_instructions" : "True" if self.show_instructions else "False",
            "test_mode" : self.test_mode,
            "graph_y_max" : self.graph_y_max,
            "parameter_set_zone_minutes" : [p.json() for p in self.parameter_set_zone_minutes.all()],
            "consent_form" : self.consent_form,
            "consent_form_required" : self.consent_form_required,
        }

