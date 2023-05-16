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
from main.globals import PayBlockType

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
    updated = models.DateTimeField(auto_now=True)

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
        return  self.start_date.strftime("%-m/%#d/%Y")
    
    def get_start_date_string_widget(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%Y-%#m-%#d")
    
    def get_end_date_string(self):
        '''
        get a formatted string of end date
        '''
        return  self.end_date.strftime("%-m/%#d/%Y")

    def start_experiment(self):
        '''
        setup and start experiment
        '''

        logger = logging.getLogger(__name__) 

        self.started = True
        self.finished = False     
        
        self.parameter_set.json_for_subject(update_required=True)

        session_periods = []

        period_date = self.start_date

        #create session periods
        for i, p in enumerate(self.parameter_set.parameter_set_periods.all()):
            session_periods.append(main.models.SessionPeriod(session=self, parameter_set_period=p, period_number=i+1, period_date=period_date))
            period_date += timedelta(days=1)

        #logger.info(f"Session Periods Created")
        
        main.models.SessionPeriod.objects.bulk_create(session_periods)

        #set last day of each pay block parameter_set_periods_b
        for i in self.parameter_set.parameter_set_pay_blocks_a.all():
            parameter_set_period = i.parameter_set_periods_b.last()

            if parameter_set_period:
                session_period = self.session_periods.get(parameter_set_period=parameter_set_period)
                session_period.is_last_period_in_block = True
                session_period.save()

        self.current_experiment_phase = ExperimentPhase.RUN

        self.save()

        for i in self.session_players.all():
            i.start()
            # logger.info(f"Player {i} Created")
    
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
        
        session_period = self.session_periods.filter(period_date=todays_date()).prefetch_related('parameter_set_period')
        
        return session_period.first()

    def get_yesterday_session_period(self):
        '''
        return the current session period
        '''
        if not self.started:
            return None
        
        session_period_today = self.get_current_session_period()

        if not session_period_today:
            return None
        
        session_period_yesterday = self.session_periods.filter(period_number=session_period_today.period_number-1)

        return session_period_yesterday.first()
    
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
            new_session_player.player_key_backup = new_session_player.player_key

            new_session_player.save()

    def get_download_summary_csv(self):
        '''
        return data summary in csv format
        '''

        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            writer.writerow(["Session ID", "Pay Block Type", "Pay Block Number", "Period", "Player", "Note", "Recruiter ID", "Label", "Group", "Device", 
                            "Zone Minutes", "Average Block Zone Minutes", "Peak Minutes", "Cardio Minutes", "Fat Burn Minutes", "Out of Range Minutes", "Zone Minutes HR BPM Reported", "Zone Minutes HR BPM Expected", "Resting HR", "Age", "Wrist Time", 
                            "Checked In", "Checked In Forced", "Fixed Pay", "Individual Earnings", "Group Earnings", "Earnings Paid", "Fitbit Earned Percent", "Total Fitbit Earned Percent", "Last Visit Time",
                            "Calories", "Steps", "Minutes Sedentary", "Minutes Lightly Active", "Minutes Fairly Active", "Minutes Very Active"])

            for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
                for s_p in p.session_player_periods_a.filter(session_player__soft_delete=False).order_by('session_player__group_number', 'session_player__player_number'):
                    s_p.write_summary_download_csv(writer)

            v = output.getvalue()
            output.close()

        return v
    
    def get_download_heart_rate_csv(self):
        '''
        return heart rate data in csv format
        '''

        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            v = ["Session ID", "Period", "Player", "Note", "Recruiter ID", "Group"]

            for i in range(1440):
                v.append(str(timedelta(minutes=i)))

            writer.writerow(v)

            for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
                for s_p in p.session_player_periods_a.filter(session_player__soft_delete=False).order_by('session_player__group_number', 'session_player__player_number'):
                    s_p.write_heart_rate_download_csv(writer)

            v = output.getvalue()
            output.close()

        return v
    
    def get_download_activities_csv(self):
        '''
        return activities data recruiter in csv format
        '''

        with io.StringIO() as output:
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            v = ["Session ID", "Period", "Player", "Note", "Recruiter ID", "Group", "Activity", "Zone Minutes", "Start Time", "End Time", "Log Type"]

            writer.writerow(v)

            for p in self.session_periods.all().prefetch_related('session_player_periods_a'):
                for s_p in p.session_player_periods_a.filter(session_player__soft_delete=False).order_by('session_player__group_number', 'session_player__player_number'):
                    s_p.write_activities_download_csv(writer)

            v = output.getvalue()
            output.close()

        return v
    
    def get_download_chat_csv(self):
        '''
        return chat data in csv format
        '''

        with io.StringIO() as output:
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            v = ["Session ID", "Period", "Player", "Recruiter ID", "Group", "Chat", "Timestamp"]
    
            writer.writerow(v)

            chat_list = main.models.SessionPlayerChat.objects.filter(session_player__in=self.session_players.all()) \
                                                            .filter(session_player__soft_delete=False)\
                                                            .select_related('session_period', 'session_player') \
                                                            .order_by('session_player__group_number', 'timestamp')

            for c in chat_list:
                c.write_action_download_csv(writer)

            v = output.getvalue()
            output.close()

        return v
    
    def get_payblock_data_csv(self):
        '''
        return payblock level data in csv format
        '''

        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

            v = ["Session ID", "Payblock Number","Payblock Type", "Player", "Note", "Recruiter ID", "Group", 
                "Total Zone Minutes", "Average Zone Minutes", "Median Zone Minutes",
                "Fixed Pay", "Individual Bonus", "Group Bonus", "Fitbit Percent","Check-ins"]
    
            writer.writerow(v)

            for i in self.parameter_set.parameter_set_pay_blocks_a.all():
                for j in self.session_players.filter(soft_delete=False):
                    j.write_payblock_csv(i, writer)

            v = output.getvalue()
            output.close()

        return v

    def get_no_checkins_csv(self):
        '''
        return no checkins for todays session period
        '''
        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONE)

            session_period = self.get_current_session_period()

            if session_period:
                for i in session_period.session_player_periods_a.filter(check_in=False):
                    if i.session_player.email:
                        writer.writerow([i.session_player.email])                 

            v = output.getvalue()
            output.close()

        return v
    
    def get_playerlist_csv(self):
        '''
        return the player list in csv format
        '''

        with io.StringIO() as output:

            writer = csv.writer(output, quoting=csv.QUOTE_NONE)

            for i in self.session_players.filter(soft_delete=False):
                v = [i.name,
                    "",
                    i.email, 
                    i.student_id, 
                    i.recruiter_id_private, 
                    i.recruiter_id_public]

                writer.writerow(v)

            v = output.getvalue()
            output.close()

        return v

    def fill_with_test_data(self):
        '''
        fill session players with test data up to this point in the experiment
        '''

        if self.is_before_first_period():
            return

        period = self.get_current_session_period()

        if not period:
            period = self.session_periods.last()

        for p in self.session_players.all():
            p.fill_with_test_data(period.period_number)
        
        for p in self.session_players.all():
            for i in self.parameter_set.parameter_set_pay_blocks_a.all():
                p.calc_averages_for_block(i)

        for p in self.session_players.all():
            for i in self.parameter_set.parameter_set_pay_blocks_a.all():
                p.calc_payments_for_block(i)

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

        session_periods = self.session_periods.filter(parameter_set_period__parameter_set_pay_block=pay_block)

        if session_periods:
            return {"start_day" : session_periods.first().json(),
                    "end_day" : session_periods.last().json()}
        else:
            return {"start_day" : {},
                    "end_day" : {}}

    def get_pay_block(self, pay_block, get_payments=True):
        '''
        return dict of payblocks
        '''

        pay_block_json = {"block_number" : pay_block.pay_block_number,
                          "range" : self.get_pay_block_range(pay_block),
                          "payments" : []} 

        if get_payments:
            for p in self.session_players.exclude(disabled=True).exclude(soft_delete=True):

                payment = {"recruiter_id_private" : p.recruiter_id_private, 
                           "student_id" : p.student_id,
                           "earnings" : p.get_block_earnings(pay_block)}
                
                pay_block_json["payments"].append(payment)

        return pay_block_json
    
    def get_pay_block_csv(self, pay_block_number):
        '''
        return pay block in csv format
        '''

        parameter_set_pay_block = self.parameter_set.parameter_set_pay_blocks_a.get(pay_block_number=pay_block_number)

        pay_block = self.get_pay_block(parameter_set_pay_block)

        
        with io.StringIO() as output:
            writer = csv.writer(output, quoting=csv.QUOTE_NONE)

            if parameter_set_pay_block.pay_block_type == PayBlockType.EARN_FITBIT:
                for p in pay_block["payments"]:
                    writer.writerow([p["student_id"], p["earnings"]["earnings_no_pay_percent"]])
            else:
                for p in pay_block["payments"]:
                    writer.writerow([p["recruiter_id_private"], p["earnings"]["total"]])

            v = output.getvalue()
            output.close()

        return v
    
    def get_pay_block_list(self):
        '''
        return a list of pay_blocks
        '''

        pay_blocks = {}

        for p in self.parameter_set.parameter_set_pay_blocks_a.all():

            if not pay_blocks.get(p.pay_block_number, False):
                pay_blocks[p.pay_block_number] = self.get_pay_block(p, False)

        return pay_blocks
    
    def back_fill_for_pay_block(self, pay_block_number):
        '''
        back fill last day of a pay block
        '''

        parameter_set_pay_block = self.parameter_set.parameter_set_pay_blocks_a.get(pay_block_number=pay_block_number)
        
        for i in self.session_players.exclude(disabled=True):

            pull_list = i.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=parameter_set_pay_block, back_pull=False)

            if pull_list:

                p = pull_list.last()

                i.pull_todays_metrics(p)

            for p in pull_list:
                if p.check_in:
                    p.take_check_in(False)

        for i in self.session_players.exclude(disabled=True):
            i.calc_averages_for_block(parameter_set_pay_block)
        
        for i in self.session_players.exclude(disabled=True):
            i.calc_payments_for_block(parameter_set_pay_block)

    def get_group_channel_list(self, group_number):
        '''
        return list of channels ids for specified group
        '''
        return [p.channel_name for p in self.session_players.filter(group_number=group_number)]
    
    def auto_assign_groups(self):
        '''
        auto assign gruops to session players based on parameter set group size.
        '''
        temp_group = 1
        temp_counter = 0

        for i in self.session_players.all():
            i.group_number = temp_group
            i.save()
            temp_counter+=1

            if temp_counter == self.parameter_set.group_size:
                temp_group += 1
                temp_counter = 0

    def import_connections(self, session_id):
        '''
        import player connections from another session
        '''

        try:
            session_source = main.models.Session.objects.get(id=session_id)
        except ObjectDoesNotExist:            
            return {"value":"fail", "result":"session not found"}

        for i in self.session_players.all():
            player_source = session_source.session_players.filter(email=i.email)

            if player_source:
                player_source_first = player_source.first()
                i.fitbit_user_id = player_source_first.fitbit_user_id

                player_source_first.player_key_backup = player_source_first.player_key
                player_source_first.save()

                i.player_key_backup = i.player_key
                i.save()

                i.player_key = player_source_first.player_key
                i.note = player_source_first.note
                player_source_first.player_key = uuid.uuid4()

                player_source_first.save()
                i.save()
        
        return {"value":"success"}

    def user_is_owner(self, user):
        '''
        return turn is user is owner or an admin
        '''

        if user.is_staff:
            return True

        if user==self.creator:
            return True
        
        return False
    
    def json(self):
        '''
        return json object of model
        '''

        logger = logging.getLogger(__name__)

        start_load_time = datetime.now()

        current_session_period = self.get_current_session_period()
        yesterday_session_period = self.get_yesterday_session_period()

        if self.is_after_last_period():
            current_session_period = self.session_periods.last()

        is_last_period = False
        if current_session_period:
            if current_session_period == self.session_periods.last():
                is_last_period = True
        
        current_parameter_set_period = self.parameter_set.json()['parameter_set_periods'][str(current_session_period.parameter_set_period.id)] if current_session_period else None,

        v = {
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "start_date_widget":self.get_start_date_string_widget(),
            "end_date":self.get_end_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,

            "current_parameter_set_period": current_parameter_set_period,
            
            "current_period" : current_session_period.json() if current_session_period else None,
            "yesterdays_period" : yesterday_session_period.json() if yesterday_session_period else None,

            "median_zone_minutes" : [i.get_median_average_zone_minutes() for i in self.session_periods.all()],

            "finished":self.finished,
            "parameter_set": self.parameter_set.json(),
            "session_players":[i.json_min() for i in self.session_players.filter(soft_delete=False)],
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "is_before_first_period" : self.is_before_first_period(),
            "is_after_last_period" : self.is_after_last_period(),
            "is_last_period": is_last_period, 
            "pay_blocks" : self.get_pay_block_list(),
        }

        logger.info(f'Session JSON Load Length:{datetime.now() - start_load_time}' )

        return v

    def json_for_parameter_set(self):
        '''
        json for parameter set setup screen
        '''

        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "started":self.started,
            "parameter_set": self.parameter_set.json(),
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

        current_parameter_set_period = current_session_period.parameter_set_period.json_for_subject() if current_session_period else None

        if(current_parameter_set_period):
            current_parameter_set_period["notice_text"] = session_player.process_help_doc(current_parameter_set_period["notice_text"])


        parameter_set_json_for_subject = self.parameter_set.json_for_subject()

        #hide future pay blocks
        if(current_parameter_set_period):
            for i in parameter_set_json_for_subject["parameter_set_pay_blocks"]:
                if parameter_set_json_for_subject["parameter_set_pay_blocks"][i]["pay_block_number"] > current_parameter_set_period["parameter_set_pay_block"]["pay_block_number"]:
                    parameter_set_json_for_subject["parameter_set_pay_blocks"][i] = {}
        else:
            parameter_set_json_for_subject["parameter_set_pay_blocks"] = {}

        return{
            "id":self.id,
            "started":self.started,
            "start_date":self.get_start_date_string(),
            "current_experiment_phase":self.current_experiment_phase,
            
            "current_parameter_set_period": current_parameter_set_period,
            "current_period"  : current_session_period.period_number if current_session_period else "---",
            "current_period_day_of_week": current_session_period.get_formatted_day_of_week_full() if current_session_period else "---",

            "enable_chat" : self.parameter_set.enable_chat,

            "finished":self.finished,

            "parameter_set":parameter_set_json_for_subject,
            "is_before_first_period" : self.is_before_first_period(),
            "is_after_last_period" : self.is_after_last_period(),
            "is_last_period": is_last_period, 

            "session_players":[i.json_for_subject(session_player) for i in session_player.session.session_players.filter(group_number=session_player.group_number).prefetch_related()],
        }
          
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()
