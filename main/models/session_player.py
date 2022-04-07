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

    fitbit_user_id = models.CharField(max_length=100, default="",verbose_name = 'FitBit User ID')                #fitbit user id

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
        self.fitbit_user_id = ""

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

    def get_session_player_periods_1_json(self):
        '''
        return current session player periods
        '''
        current_session_period = self.session.get_current_session_period()

        if current_session_period:
            current_parameter_set_period = current_session_period.parameter_set_period

            if not current_parameter_set_period.show_graph_1:
                return []

            session_player_periods = self.session_player_periods_b.filter(session_period__period_number__gte=current_parameter_set_period.graph_1_start_period_number) \
                                                                  .filter(session_period__period_number__lte=current_parameter_set_period.graph_1_end_period_number)
            return [p.json_for_subject() for p in session_player_periods] 
        
        return []
    
    def get_session_player_periods_2_json(self):
        '''
        return current session player periods for graph 2
        '''
        current_session_period = self.session.get_current_session_period()

        if current_session_period:
            current_parameter_set_period = current_session_period.parameter_set_period

            if not current_parameter_set_period.show_graph_2:
                return []

            session_player_periods = self.session_player_periods_b.filter(session_period__period_number__gte=current_parameter_set_period.graph_2_start_period_number) \
                                                                  .filter(session_period__period_number__lte=current_parameter_set_period.graph_2_end_period_number)
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
        
        pay_group_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block,
                                                                        check_in=True)

        for p in pay_group_player_periods:
            total += p.earnings_individual

        return total

    def get_pay_block_bonus_earnings(self, pay_block):
        '''
        return the group bonus earnings from the specified pay_block
        '''    
        total = 0

        pay_group_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block,
                                                                        check_in=True)

        for p in pay_group_player_periods:
            total += p.earnings_group

        return total
    
    def get_pay_block_range(self, pay_block):
        '''
        return the day range of the pay_block
        '''

        pay_group_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block)

        return {"start_day" : pay_group_player_periods.first().session_period.period_number, "end_day" : pay_group_player_periods.last().session_period.period_number}

    def get_current_block_earnings(self):
        '''
        return current payblock earnings
        '''

        current_session_period = self.session.get_current_session_period()

        earnings = {"individual":"0.00", 
                    "group_bonus":"0.00", 
                    "total":"0.00",
                    "range": {"start_day":"---", "end_day":"---"}}

        if not current_session_period:
            return earnings

        pay_block = current_session_period.parameter_set_period.pay_block
        
        earnings["individual"] = self.get_pay_block_individual_earnings(pay_block)
        earnings["group_bonus"] = self.get_pay_block_bonus_earnings(pay_block)
        earnings["total"] = earnings["individual"] + earnings["group_bonus"]
        earnings["range"] = self.get_pay_block_range(pay_block)

        return earnings
    
    def get_todays_session_player_period(self):
        '''
        return the session player period for today
        '''
        return self.session_player_periods_b.filter(session_period=self.session.get_current_session_period()).first()
    
    def get_yesterdays_session_player_period(self):
        '''
        return the session player period for yesterday
        '''

        current_session_period = self.session.get_current_session_period()

        if not current_session_period:
            return None

        return self.session_player_periods_b.filter(session_period__period_number=current_session_period.period_number-1).first()
    
    def pull_todays_metrics(self):
        '''
        pull needed metrics from yesterday and today
        '''

        todays_session_player_period = self.get_todays_session_player_period()

        if todays_session_player_period:
            r = todays_session_player_period.pull_fitbit_heart_time_series()

            if r["status"] == "fail":
                return r
        
        yesterdays_session_player_period = self.get_yesterdays_session_player_period()

        if yesterdays_session_player_period:
            r = yesterdays_session_player_period.pull_fitbit_heart_time_series()

            if r["status"] == "fail":
                return r
        
        return {"status" : "success", "message" : ""}
        
    def json(self, get_chat=True):
        '''
        json object of model
        '''
        todays_session_player_period = self.get_todays_session_player_period()

        chat_all = []
        if self.session.parameter_set.enable_chat:
            chat_all = [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)
                                                                                   .order_by('-timestamp')[:100:-1]
                       ] if get_chat else [],
        
        session_player_periods_group_1_json = []

        for p in self.session.session_players.exclude(id=self.id).filter(group_number=self.group_number):
            session_player_periods_group_1_json.append(p.get_session_player_periods_1_json())
        
        session_player_periods_group_2_json = []

        for p in self.session.session_players.exclude(id=self.id).filter(group_number=self.group_number):
            session_player_periods_group_2_json.append(p.get_session_player_periods_2_json())

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

            "session_player_periods_1" : self.get_session_player_periods_1_json(),
            "session_player_periods_2" : self.get_session_player_periods_2_json(),

            "session_player_periods_1_group" : session_player_periods_group_1_json,
            "session_player_periods_2_group" : session_player_periods_group_2_json,

            "current_block_earnings" : self.get_current_block_earnings(),

            "checked_in_today" : todays_session_player_period.check_in if todays_session_player_period else None,
            "group_checked_in_today" : todays_session_player_period.group_checked_in_today() if todays_session_player_period else False,

            "individual_earnings" : todays_session_player_period.get_individual_parameter_set_payment() if todays_session_player_period else None,
            "group_earnings" : todays_session_player_period.get_group_parameter_set_payment() if todays_session_player_period else False,
        }
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

        todays_session_player_period = self.get_todays_session_player_period()

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
            "session_player_periods_1" : self.get_session_player_periods_1_json(),
            "session_player_periods_2" : self.get_session_player_periods_2_json(),
            "parameter_set_player" : self.parameter_set_player.json(),
            "current_block_earnings" : self.get_current_block_earnings(),
            "checked_in_today" : todays_session_player_period.check_in if todays_session_player_period else None,
            "group_checked_in_today" : todays_session_player_period.group_checked_in_today() if todays_session_player_period else False,
        }

    def json_min(self):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,    
        }


        