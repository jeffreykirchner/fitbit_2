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
from main.globals import todays_date

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
    
    def get_start_date_string_widget(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%Y-%#m-%#d")
    
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

        self.current_experiment_phase = ExperimentPhase.RUN

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
        
        session_period = self.session_periods.filter(period_date=todays_date())

        return session_period.first()
    
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

        writer.writerow(["Session ID", "Period", "Player", "Group", 
                         "Zone Minutes", "Sleep Minutes", "Peak Minutes", "Cardio Minutes", "Fat Burn Minutes", "Out of Range Minutes", "Zone Minutes HR BPM", "Wrist Time", 
                         "Checked In", "Checked In Forced", "Individual Earnings", "Group Earnings", "Total Earnings", "Last Visit Time"])

        for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
            for s_p in p.session_player_periods_a.all().order_by('session_player__group_number', 'session_player__player_number'):
                s_p.write_summary_download_csv(writer)

        return output.getvalue()
    
    def get_download_heart_rate_csv(self):
        '''
        return heart rate data in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        v = ["Session ID", "Period", "Player", "Group"]

        for i in range(1440):
            v.append(str(timedelta(minutes=i)))

        writer.writerow(v)

        for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
            for s_p in p.session_player_periods_a.all().order_by('session_player__group_number', 'session_player__player_number'):
                s_p.write_heart_rate_download_csv(writer)

        return output.getvalue()
    
    def get_download_activities_csv(self):
        '''
        return activities data recruiter in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        v = ["Session ID", "Period", "Player", "Group", "Activity", "Zone Minutes", "Start Time", "End Time", "Log Type"]

        writer.writerow(v)

        for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
            for s_p in p.session_player_periods_a.all().order_by('session_player__group_number', 'session_player__player_number'):
                s_p.write_activities_download_csv(writer)

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
    
    def fill_with_test_data(self):
        '''
        fill session players with test data up to this point in the experiment
        '''

        period = self.get_current_session_period()

        if not period:
            return

        for p in self.session_players.all():
            p.fill_with_test_data(period.period_number)

    def is_before_first_period(self):
        '''
        return true if today's date is before the first period
        '''
        session_period = self.session_periods.first()

        if not session_period:
            return True

        today = todays_date().date()

        if today < session_period.period_date:
            return True
        
        return False

    def is_after_last_period(self):
        '''
        return true if today's date is after the last period
        '''

        session_period = self.session_periods.last()

        if not session_period:
            return False

        if todays_date().date() > session_period.period_date:
            return True
        
        return False

    def get_pay_block_range(self, pay_block):
        '''
        return the day range of the pay_block
        '''

        session_periods = self.session_periods.filter(parameter_set_period__pay_block=pay_block)

        if session_periods:
            return {"start_day" : session_periods.first().json(),
                    "end_day" : session_periods.last().json()}
        else:
            return {"start_day" : {},
                    "end_day" : {}}

    def get_pay_block(self, pay_block_number):
        '''
        return dict of payblocks
        '''

        pay_block = {"block_number" : pay_block_number,
                     "range" : self.get_pay_block_range(pay_block_number),
                     "payments" : []} 

        for p in self.session_players.all():

            payment = {"student_id" : p.student_id, "earnings" : p.get_block_earnings(pay_block_number)}
            pay_block["payments"].append(payment)

        return pay_block
    
    def get_pay_block_csv(self, pay_block_number):
        '''
        return pay block in csv format
        '''
        pay_block = self.get_pay_block(pay_block_number)

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONE)
       
        for p in pay_block["payments"]:
            writer.writerow([p["student_id"], p["earnings"]["total"]])

        return output.getvalue()
    
    def get_pay_block_list(self):
        '''
        return a list of pay_blocks
        '''

        pay_blocks = {}

        for p in self.parameter_set.parameter_set_periods.all():
            if not pay_blocks.get(str(p.pay_block), False):
                pay_blocks[str(p.pay_block)] = self.get_pay_block(p.pay_block)

        return pay_blocks
    
    def back_fill_for_pay_block(self, pay_block_number):
        '''
        back fill last day of a pay block
        '''
        
        for i in self.session_players.all():

            p = i.session_player_periods_b.filter(session_period__parameter_set_period__pay_block=pay_block_number).last()

            if not p.back_pull:

                p.back_pull=True
                p.save()

                if p.check_in:
                    p.take_check_in(False)
                else:
                    p.pull_secondary_metrics(False)

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

        current_session_period = self.get_current_session_period()

        is_last_period = False
        if current_session_period:
            if current_session_period == self.session_periods.last():
                is_last_period = True

        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "start_date_widget":self.get_start_date_string_widget(),
            "end_date":self.get_end_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,

            "current_parameter_set_period": current_session_period.parameter_set_period.json() if current_session_period else None,
            "current_period" : current_session_period.period_number if current_session_period else "---",
            "current_period_day_of_week": current_session_period.get_formatted_day_of_week_full() if current_session_period else "---",

            "finished":self.finished,
            "parameter_set":self.parameter_set.json(),
            "session_players":[i.json_for_staff() for i in self.session_players.all()],
            "chat_all" : chat,
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "is_before_first_period" : self.is_before_first_period(),
            "is_after_last_period" : self.is_after_last_period(),
            "is_last_period": is_last_period, 
            "pay_blocks" : self.get_pay_block_list(),
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''

        current_session_period = self.get_current_session_period()

        is_last_period = False
        if current_session_period:
            if current_session_period == self.session_periods.last():
                is_last_period = True

        return{
            "id":self.id,
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            
            "current_parameter_set_period": current_session_period.parameter_set_period.json() if current_session_period else None,
            "current_period"  : current_session_period.period_number if current_session_period else "---",
            "current_period_day_of_week": current_session_period.get_formatted_day_of_week_full() if current_session_period else "---",

            "finished":self.finished,

            "parameter_set":self.parameter_set.json_for_subject(),
            "is_before_first_period" : self.is_before_first_period(),
            "is_after_last_period" : self.is_after_last_period(),
            "is_last_period": is_last_period, 

            "session_players":[i.json_for_subject(session_player) for i in session_player.session.session_players.filter(group_number=session_player.group_number)],
        }
          
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()
