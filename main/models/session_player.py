'''
session player model
'''

#import logging
import uuid
import logging

from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayer

from main.globals import round_half_away_from_zero

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")

    player_number = models.IntegerField(verbose_name='Player number', default=0)                        #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')      #login and channel key
    connecting = models.BooleanField(default=False, verbose_name='Consumer is connecting')              #true when a consumer is connceting
    connected_count = models.IntegerField(verbose_name='Number of consumer connections', default=0)     #number of consumers connected to this subject

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="")                     #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="")              #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True, null=True)              #subject's email address
                                         
    group_number = models.IntegerField(default = 1, verbose_name="Group Number")

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

    disabled =  models.BooleanField(default=False)                                                   #if true disable subject's screen

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['player_number']
        constraints = [            
            models.UniqueConstraint(fields=['session', 'email'], name='unique_email_session_player', condition=~Q(email="")),
        ]

    def reset(self):
        '''
        reset player to starting state
        '''

        self.name = ""
        self.student_id = ""
        self.email = None

        self.save()
    
    def start(self):
        '''
        start experiment
        '''

        self.reset()

        #session player periods
        session_player_periods = []

        for i in self.session.session_periods.all():
            session_player_periods.append(main.models.SessionPlayerPeriod(session_period=i, session_player=self))
        
        main.models.SessionPlayerPeriod.objects.bulk_create(session_player_periods)

    def get_instruction_set(self):
        '''
        return a proccessed list of instructions to the subject
        '''

        instructions = [i.json() for i in self.parameter_set_player.parameter_set.instruction_set.instructions.all()]
 
        for i in instructions:
            i["text_html"] = i["text_html"].replace("#player_number#", self.parameter_set_player.id_label)
            i["text_html"] = i["text_html"].replace("#player_count-1#", str(self.parameter_set_player.parameter_set.parameter_set_players.count()-1))

        return instructions

    def get_session_player_periods_json(self):
        '''
        return current session player periods
        '''

        current_session_period = self.session.get_current_session_period()

        if current_session_period:
            current_parameter_set_period = current_session_period.parameter_set_period

            session_player_periods = self.session_player_periods_b.filter(session_period__period_number__gte=current_parameter_set_period.graph_1_start_period_number) \
                                                                  .filter(session_period__period_number__lte=current_parameter_set_period.graph_1_end_period_number)
            return [p.json_for_subject() for p in session_player_periods] 
        
        return []

    def fill_with_test_data(self, period):
        '''
        fill session player with test data up to, but not including period
        '''

        for p in self.session_player_periods_b.filter(session_period__period_number__lt = period):
            p.fill_with_test_data()

    def get_pay_block_individual_earnings(self, pay_block):
        '''
        return the individual earnings from the specified pay_block
        '''
        total = 0
        
        pay_group_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block)

        for p in pay_group_player_periods:
            total += p.earnings_individual

        return total

    def get_pay_block_bonus_earnings(self, pay_block):
        '''
        return the group bonus earnings from the specified pay_block
        '''    
        total = 0

        pay_group_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block)

        for p in pay_group_player_periods:
            total += p.earnings_group

        return total
    
    def get_current_block_earnings(self):
        '''
        return current payblock earnings
        '''

        current_session_period = self.session.get_current_session_period()

        earnings = {"individual":"0.00", "group_bonus":"0.00", "total":"0.00"}

        if not current_session_period:
            return earnings
        
        earnings["individual"] = self.get_pay_block_individual_earnings(current_session_period.parameter_set_period.pay_block)
        earnings["group_bonus"] = self.get_pay_block_bonus_earnings(current_session_period.parameter_set_period.pay_block)
        earnings["total"] = earnings["individual"] + earnings["group_bonus"]

        return earnings
    
    def json(self, get_chat=True):
        '''
        json object of model
        '''
        chat_all = []
        if self.session.parameter_set.enable_chat:
            chat_all = [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)
                                                                                   .order_by('-timestamp')[:100:-1]
                       ] if get_chat else [],
        
        session_player_periods_group_json = []

        for p in self.session.session_players.exclude(id=self.id).filter(group_number=self.group_number):
            session_player_periods_group_json.append(p.get_session_player_periods_json())

        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "group_number" : self.group_number,

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.json(),

            "chat_all" : chat_all,
            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

            "session_player_periods" : self.get_session_player_periods_json(),
            "session_player_periods_group" : session_player_periods_group_json,

            "current_block_earnings" : self.get_current_block_earnings(),
        }
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

        chat_individual = []

        if self.session.parameter_set.enable_chat:
            chat_individual = [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects \
                                                                            .filter(chat_type=main.globals.ChatTypes.INDIVIDUAL) \
                                                                            .filter(Q(Q(session_player_recipients=session_player) & Q(session_player=self)) |
                                                                                    Q(Q(session_player_recipients=self) & Q(session_player=session_player)))
                                                                            .order_by('-timestamp')[:100:-1]
                                ],

        return{
            "id" : self.id,  

            "player_number" : self.player_number,
            "chat_individual" :chat_individual,
            "new_chat_message" : False,
            "parameter_set_player" : self.parameter_set_player.json_for_subject(),
            "session_player_periods" : self.get_session_player_periods_json(),
            "parameter_set_player" : self.parameter_set_player.json(),
            "current_block_earnings" : self.get_current_block_earnings(),
        }

    def json_min(self):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,    
        }


        