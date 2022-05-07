'''
session player chat
'''

#import logging
import pytz

from django.db import models
from django.db.models import Q
from django.db.models import F

from main.models import SessionPlayer
from main.models import SessionPeriod

from main.globals import todays_date

import main

class SessionPlayerChat(models.Model):
    '''
    session player move model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_chats_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_chats_b")

    text = models.CharField(max_length = 1000, default="Chat here", verbose_name="Chat Text")       #chat text
    show_time_stamp = models.BooleanField(default=False)                                            #show time stamp in chat box if this is true        

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player Chat'
        verbose_name_plural = 'Session Player Chats'
        ordering = ['timestamp']
        constraints = [
             models.CheckConstraint(check=~Q(text=''), name='text_not_empty'),
        ]

    def write_action_download_csv(self, writer):
        '''
        take csv writer and add row
        '''        

        # ["Session ID", "Period", "Player", "Group", "Chat", "Timestamp"]

        prm = main.models.Parameters.objects.first()
        tmz = pytz.timezone(prm.experiment_time_zone) 
       
        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.group_number,
                         self.text,
                         self.timestamp.astimezone(tmz).strftime("%m/%d/%Y %I:%M:%S %p")])

    def json_csv(self):
        '''
        json object for csv download
        '''
        return{

            "sender_client_number" : self.session_player.player_number,

            "text" : self.text,
            
        }

    def json_for_subject(self):
        '''
        json object of model
        '''

        time_stamp_text = ""

        if self.show_time_stamp:
            prm = main.models.Parameters.objects.first()
            tmz = pytz.timezone(prm.experiment_time_zone) 
            
            timestamp_tmz =  self.timestamp.astimezone(tmz)

            if timestamp_tmz.date() == todays_date().date():
                time_stamp_text = "Today " + timestamp_tmz.strftime("%-I:%M %p")
            else:
                time_stamp_text = timestamp_tmz.strftime("%-m/%-d/%Y %-I:%M %p")

        return{
            "id" : self.id,    
            "sender_label" : self.session_player.parameter_set_player.id_label,
            "sender_color" : self.session_player.parameter_set_player.display_color,  
            "sender_id" : self.session_player.id,    
            "text" : self.text,
            "show_time_stamp" : self.show_time_stamp,
            "time_stamp_text" : time_stamp_text,
        }
        
    #return json object of class
    def json_for_staff(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,       
            "send_id" : self.session_player.id,  
            "sender_label" : self.session_player.parameter_set_player.id_label,
            "text" : self.text,
        }
        