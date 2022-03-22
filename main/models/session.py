'''
session model
'''

from datetime import datetime
from datetime import timedelta
from tinymce.models import HTMLField

import logging
import uuid
import csv
import io
import pytz

from django.conf import settings

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

import main

from main.models import ParameterSet

from main.globals import ExperimentPhase

#experiment sessoin
class Session(models.Model):
    '''
    session model
    '''
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_a")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="sessions_b")

    title = models.CharField(max_length = 300, default="*** New Session ***")    #title of session
    start_date = models.DateField(default=now)                                   #date of session start
    end_date = models.DateField(default=now)                                     #date of session end

    current_experiment_phase = models.CharField(max_length=100, choices=ExperimentPhase.choices, default=ExperimentPhase.RUN)         #current phase of expeirment

    channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    started =  models.BooleanField(default=False)                                #starts session and filll in session
    finished = models.BooleanField(default=False)                                #true after all session periods are complete

    shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    canceled = models.BooleanField(default=False)                                #true if session needs to be canceled
    cancelation_text =  models.CharField(max_length=10000, default="")           #text sent to subjects if experiment is canceled
    cancelation_text_subject = models.CharField(max_length=1000, default="")     #email subject text for experiment cancelation

    invitation_text = HTMLField(default="", verbose_name="Invitation Text")       #inviataion email subject and text
    invitation_subject = HTMLField(default="", verbose_name="Invitation Subject")

    soft_delete =  models.BooleanField(default=False)                            #hide session if true

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def creator_string(self):
        return self.creator.email
    creator_string.short_description = 'Creator'

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_date']

    def get_start_date_string(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%#m/%#d/%Y")
    
    def get_end_date_string(self):
        '''
        get a formatted string of end date
        '''
        return  self.end_date.strftime("%#m/%#d/%Y")

    def start_experiment(self):
        '''
        setup and start experiment
        '''

        self.started = True
        self.finished = False     

        session_periods = []

        period_date = self.start_date

        for i, p in enumerate(self.parameter_set.parameter_set_periods.all()):
            session_periods.append(main.models.SessionPeriod(session=self, parameter_set_period=p, period_number=i+1, period_date=period_date))
            period_date += timedelta(days=1)
        
        main.models.SessionPeriod.objects.bulk_create(session_periods)

        self.save()

        for i in self.session_players.all():
            i.start()
    
    def update_end_date(self):
        '''
        update end date
        '''
        self.end_date = self.start_date +  timedelta(days=self.parameter_set.parameter_set_periods.count()-1)
        self.save()
 
    def reset_experiment(self):
        '''
        reset the experiment
        '''
        self.started = False
        self.finished = False

        for p in self.session_players.all():
            p.reset()

        self.save()
        self.session_periods.all().delete()
    
    def reset_connection_counts(self):
        '''
        reset connection counts
        '''
        self.session_players.all().update(connecting=False, connected_count=0)
    
    def get_current_session_period(self):
        '''
        return the current session period
        '''
        if not self.started:
            return None
        
        parameter_set_period = self.session_periods.filter(period_date=datetime.now(pytz.UTC))

        return parameter_set_period.first()
    
    def update_player_count(self):
        '''
        update the number of session players based on the number defined in the parameterset
        '''

        self.session_players.all().delete()
    
        for count, i in enumerate(self.parameter_set.parameter_set_players.all()):
            new_session_player = main.models.SessionPlayer()

            new_session_player.session = self
            new_session_player.parameter_set_player = i
            new_session_player.player_number = count + 1

            new_session_player.save()

    def get_download_summary_csv(self):
        '''
        return data summary in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["Session ID", "Period", "Client #", "Label", "Earnings ¢"])

        session_player_periods = main.models.SessionPlayerPeriod.objects.filter(session_player__in=self.session_players.all()) \
                                                                        .order_by('session_period__period_number')

        for p in session_player_periods.all():
            p.write_summary_download_csv(writer)

        return output.getvalue()
    
    def get_download_action_csv(self):
        '''
        return data actions in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["Session ID", "Period", "Time", "Client #", "Action", "Info", "Info (JSON)", "Timestamp"])

        session_player_chats = main.models.SessionPlayerChat.objects.filter(session_player__in=self.session_players.all())

        for p in session_player_chats.all():
            p.write_action_download_csv(writer)

        return output.getvalue()
    
    def get_download_recruiter_csv(self):
        '''
        return data recruiter in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        session_players = self.session_players.all()

        for p in session_players:
            writer.writerow([p.student_id, p.earnings/100])

        return output.getvalue()
    
    def get_download_payment_csv(self):
        '''
        return data payments in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow(['Name', 'Student ID', 'Earnings'])

        session_players = self.session_players.all()

        for p in session_players:
            writer.writerow([p.name, p.student_id, p.earnings/100, p.avatar.label if p.avatar else 'None'])

        return output.getvalue()
    
    def json(self):
        '''
        return json object of model
        '''

        chat = []
        if self.parameter_set.enable_chat: 
            chat = [c.json_for_staff() for c in main.models.SessionPlayerChat.objects \
                                                    .filter(session_player__in=self.session_players.all())\
                                                    .prefetch_related('session_player_recipients')
                                                    .select_related('session_player__parameter_set_player')
                                                    .order_by('-timestamp')[:100:-1]
               ]

        current_parameter_set_period = self.get_current_session_period()

        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "end_date":self.get_end_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "current_parameter_set_period": self.get_current_session_period().json() if current_parameter_set_period else None,
            "current_period" : current_parameter_set_period.period_number if current_parameter_set_period else "---",
            "finished":self.finished,
            "parameter_set":self.parameter_set.json(),
            "session_periods":[i.json() for i in self.session_periods.all()],
            "session_players":[i.json(False) for i in self.session_players.all()],
            "chat_all" : chat,
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''

        current_parameter_set_period = self.get_current_session_period()

        return{
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "current_parameter_set_period": self.get_current_session_period().json() if self.get_current_session_period() else None,
            "current_period"  : current_parameter_set_period.period_number if current_parameter_set_period else "---",
            "finished":self.finished,
            "parameter_set":self.parameter_set.json_for_subject(),

            "session_players":[i.json_for_subject(session_player) for i in session_player.session.session_players.all()]
        }
    
        
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()
