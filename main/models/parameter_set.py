'''
parameter set
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main import globals

from main.models import InstructionSet

import main

#experiment session parameters
class ParameterSet(models.Model):
    '''
    parameter set
    '''    
    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.CASCADE, related_name="parameter_sets")

    period_count = models.IntegerField(verbose_name='Number of periods', default=20)                          #number of periods in the experiment
    
    enable_chat = models.BooleanField(default=True, verbose_name = 'Private Chat')                          #if true subjects can privately chat one on one
    show_instructions = models.BooleanField(default=True, verbose_name = 'Show Instructions')                #if true show instructions

    test_mode = models.BooleanField(default=False, verbose_name = 'Test Mode')                                #if true subject screens will do random auto testing

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
            self.period_count = new_ps.get("period_count")

            self.enable_chat = new_ps.get("enable_chat")

            self.show_instructions = new_ps.get("show_instructions")

            self.save()

            
            #parameter set players
            new_parameter_set_players = new_ps.get("parameter_set_players")

            if len(new_parameter_set_players) > self.parameter_set_players.count():
                #add more players
                new_player_count = len(new_parameter_set_players) - self.parameter_set_players.count()

                for i in range(new_player_count):
                    self.add_new_player(self.parameter_set_types.first())

            elif len(new_parameter_set_players) < self.parameter_set_players.count():
                #remove excess players

                extra_player_count = self.parameter_set_players.count() - len(new_parameter_set_players)

                for i in range(extra_player_count):
                    self.parameter_set_players.last().delete()

            new_parameter_set_players = new_ps.get("parameter_set_players")
            for index, p in enumerate(self.parameter_set_players.all()):                
                p.from_dict(new_parameter_set_players[index])

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
            parameter_set_period = main.models.ParameterSetPeriod()
            parameter_set_period.parameter_set = self
            parameter_set_period.save()
        
        if self.parameter_set_players.count() == 0:
            parameter_set_player = main.models.ParameterSetPlayer()
            parameter_set_player.parameter_set = self
            parameter_set_player.save()

        pass

    def add_new_player(self):
        '''
        add a new player of type subject_type
        '''

        #24 players max
        if self.parameter_set_players.all().count() >= 24:
            return

        player = main.models.ParameterSetPlayer()
        player.parameter_set = self

        player.save()
    
    def add_new_period(self):
        '''
        add new parameter set period
        '''

        parameter_set_period = main.models.ParameterSetPeriod()

        parameter_set_period.parameter_set = self
        parameter_set_period.period_number = self.parameter_set_periods.last().period_number+1

        parameter_set_period.save()

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
            "period_count" : self.period_count,

            "enable_chat" : "True" if self.enable_chat else "False",
            "show_instructions" : "True" if self.show_instructions else "False",
            "instruction_set" : self.instruction_set.json_min(),

            "parameter_set_players" : [p.json() for p in self.parameter_set_players.all()],
            "parameter_set_periods" : [p.json() for p in self.parameter_set_periods.all()],

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
        }

