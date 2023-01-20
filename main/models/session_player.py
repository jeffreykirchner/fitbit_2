'''
session player model
'''

#import logging
from decimal import Decimal
from datetime import datetime, timedelta

import uuid
import logging
import pytz
import statistics

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayer

from main.globals import todays_date
from main.globals import get_fitbit_metrics
from main.globals import format_minutes

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")

    player_number = models.IntegerField(verbose_name='Player number', default=0)                        #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, verbose_name = 'Player Key')                      #login and channel key
    player_key_backup = models.UUIDField(default=uuid.uuid4, verbose_name = 'Player Key Backup')        #login and channel key orginally assigned
    connecting = models.BooleanField(default=False, verbose_name='Consumer is connecting')              #true when a consumer is connceting
    connected_count = models.IntegerField(verbose_name='Number of consumer connections', default=0)     #number of consumers connected to this subject
    channel_name = models.CharField(verbose_name='Django channels key', max_length = 1000, default="")  #key issued from django channels

    recruiter_id_private = models.IntegerField(verbose_name='Recruiter ID Private', default=0)          #privatly assigned id number from recruiter
    recruiter_id_public = models.UUIDField(default=uuid.uuid4, verbose_name = 'Recruiter ID Public')    #publicly assigned id number from recruiter

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="", blank=True, null=True)            #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="", blank=True, null=True)     #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True, null=True)                 #subject's email address
                                         
    group_number = models.IntegerField(default = 1, verbose_name="Group Number")

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

    fitbit_user_id = models.CharField(max_length=100, default="",verbose_name = 'FitBit User ID', blank=True, null=True)     #fitbit user id
    fitbit_last_synced = models.DateTimeField(default=None, null=True, verbose_name = 'FitBit Last Synced')                  #time when the fitbit was last synced to user's phone
    fitbit_device = models.CharField(max_length=100, default="",verbose_name = 'FitBit Device')                              #last fitbit device to sync
    
    consent_form_required = models.BooleanField(default=False, verbose_name = 'Consent Form Required')                   #consent form required

    disabled =  models.BooleanField(default=False)                                                               #if true disable subject's screen

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.player_number}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['session', 'player_number']
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
        self.consent_form_required = False
        self.disabled = False        
        self.fitbit_last_synced = None

        self.save()
    
    def start(self):
        '''
        start experiment
        '''

        self.reset()

        self.consent_form_required = self.parameter_set_player.parameter_set.consent_form_required
        self.save()

        #session player periods
        session_player_periods = []

        for i in self.session.session_periods.all():
            session_player_periods.append(main.models.SessionPlayerPeriod(session_period=i, session_player=self, survey_complete=not i.parameter_set_period.survey_required))
        
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

        for p in self.session_player_periods_b.filter(session_period__period_number__lte = period):
            p.fill_with_test_data()

    def get_pay_block_individual_earnings(self, pay_block):
        '''
        return the individual earnings from the specified pay_block
        '''

        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=pay_block)

        if session_player_periods:                                                             
            return session_player_periods.last().earnings_individual
       
        return 0

    def get_pay_block_bonus_earnings(self, pay_block):
        '''
        return the group bonus earnings from the specified pay_block
        '''    
        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=pay_block)

        if session_player_periods:                                                      
            return session_player_periods.last().earnings_group
        
        return 0
    
    def get_pay_block_fixed_earnings(self, pay_block):
        '''
        return fixed pay for 
        '''

        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=pay_block) \
                                                              .filter(check_in=True) \
                                                              .values_list('earnings_fixed', flat=True)

        if session_player_periods:
            session_player_periods = list(session_player_periods)

            return sum(session_player_periods)
        
        return 0
    
    def get_pay_block_no_pay_percent(self, pay_block):
        '''
        return the total no pay percent from all blocks
        '''

        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=pay_block) \
                                                              .filter(check_in=True) \
                                                              .values_list('earnings_no_pay_percent', flat=True)            

        if session_player_periods:
            session_player_periods = list(session_player_periods)

            return sum(session_player_periods)
        
        return 0

    def get_current_block_earnings(self):
        '''
        return current payblock earnings
        '''

        current_session_period = self.session.get_current_session_period()

        earnings = {"individual":"0", 
                    "group_bonus":"0", 
                    "fixed":"0",
                    "total":"0",
                    "earnings_no_pay_percent":"0",
                    "range": {"start_day":{}, "end_day":{}}}

        if not current_session_period:
            return earnings

        pay_block = current_session_period.parameter_set_period.parameter_set_pay_block

        earnings = self.get_block_earnings(pay_block)
        earnings["range"] = self.session.get_pay_block_range(pay_block)

        return earnings
    
    def get_block_earnings(self, pay_block):
        '''
        return dict of earnings for pay_block
        '''

        earnings = {}

        earnings["individual"] = round(self.get_pay_block_individual_earnings(pay_block))
        earnings["group_bonus"] = round(self.get_pay_block_bonus_earnings(pay_block))
        earnings["fixed"] = round(self.get_pay_block_fixed_earnings(pay_block))

        earnings["total"] = round(earnings["individual"] + earnings["group_bonus"] + earnings["fixed"])
        earnings["earnings_no_pay_percent"] = self.get_pay_block_no_pay_percent(pay_block)

        return earnings
    
    def get_block_period_count(self, parameter_set_pay_block):
        '''
        return the number of periods in payblock
        '''
        return self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=parameter_set_pay_block).count()
    
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
    
    def pull_todays_metrics(self, todays_session_player_period=None):
        '''
        pull needed metrics from yesterday and today
        '''
        logger = logging.getLogger(__name__) 
        data = {}
        session_player_periods_bp = []

        if not todays_session_player_period:
            todays_session_player_period = self.get_todays_session_player_period()    

        #if during session
        if todays_session_player_period:

            temp_date = todays_session_player_period.session_period.period_date.strftime("%Y-%m-%d")

            data["devices"] = 'https://api.fitbit.com/1/user/-/devices.json'
            data["fitbit_profile"] = f'https://api.fitbit.com/1/user/-/profile.json'

            data["fitbit_activities_td"] = f'https://api.fitbit.com/1/user/-/activities/list.json?afterDate={temp_date}&sort=asc&offset=0&limit=100'
            data["fitbit_heart_time_series_td"] = f'https://api.fitbit.com/1/user/-/activities/heart/date/{temp_date}/1d.json'


            session_player_periods_bp = self.session_player_periods_b.filter(back_pull=False) \
                                                                     .filter(session_period__period_number__lt=todays_session_player_period.session_period.period_number)\
                                                                     .order_by("-session_period__period_number")[:5]
            
            for p in session_player_periods_bp:
                temp_date = p.session_period.period_date.strftime("%Y-%m-%d")

                data[f"fitbit_activities_{p.id}"] = f'https://api.fitbit.com/1/user/-/activities/list.json?afterDate={temp_date}&sort=asc&offset=0&limit=100'
                data[f"fitbit_heart_time_series_{p.id}"] = f'https://api.fitbit.com/1/user/-/activities/heart/date/{temp_date}/1d.json'

            r = get_fitbit_metrics(self.fitbit_user_id, data)

        else:
            data['devices'] = 'https://api.fitbit.com/1/user/-/devices.json'
            r = get_fitbit_metrics(self.fitbit_user_id, data)
            if r["status"] != "fail":
                self.process_fitbit_last_synced(r["result"]["devices"]["result"])

        if r["status"] == "fail" :
            return {"status" : r['status'], "message" : r["message"]}
                    
        result = r["result"]
        if todays_session_player_period:
            todays_session_player_period.process_metrics(save_pull_time=True,
                                                         result={"devices" : result["devices"],
                                                                 "fitbit_profile" : result["fitbit_profile"],
                                                                 "fitbit_heart_time_series" : result["fitbit_heart_time_series_td"],
                                                                 "fitbit_activities" : result["fitbit_activities_td"]})

        #check synced today before storing yesterdays back pull
        if not self.fitbit_synced_today():
            return {"status" : "fail", "message" : "Not synced today"}

        for p in session_player_periods_bp:
            p.back_pull=True

            p.process_metrics(save_pull_time=False,
                              result={"fitbit_heart_time_series" : result[f"fitbit_heart_time_series_{p.id}"],
                                      "fitbit_activities" : result[f"fitbit_activities_{p.id}"]})
            p.save()

            if p.check_in:
                p.take_check_in(False)
        
        if todays_session_player_period:
            self.calc_averages_for_block(todays_session_player_period.get_pay_block())
                
        return {"status" : "success", "message" : ""}
    
    def pull_secondary_time_series(self):
        '''
        pull activity data at end of experiment
        '''
        logger = logging.getLogger(__name__)
        
        first_period_date = self.session.session_periods.first().period_date.strftime("%Y-%m-%d")
        last_period_date = self.session.session_periods.last().period_date.strftime("%Y-%m-%d")

        data = {}

        data["fitbit_steps"] = f'https://api.fitbit.com/1/user/-/activities/tracker/steps/date/{first_period_date}/{last_period_date}.json'
        data["fitbit_calories"] = f'https://api.fitbit.com/1/user/-/activities/tracker/calories/date/{first_period_date}/{last_period_date}.json'

        data["fitbit_minutes_sedentary"] = f'https://api.fitbit.com/1/user/-/activities/tracker/minutesSedentary/date/{first_period_date}/{last_period_date}.json'
        data["fitbit_minutes_lightly_active"] = f'https://api.fitbit.com/1/user/-/activities/tracker/minutesLightlyActive/date/{first_period_date}/{last_period_date}.json'
        data["fitbit_minutes_fairly_active"] = f'https://api.fitbit.com/1/user/-/activities/tracker/minutesFairlyActive/date/{first_period_date}/{last_period_date}.json'
        data["fitbit_minutes_very_active"] = f'https://api.fitbit.com/1/user/-/activities/tracker/minutesVeryActive/date/{first_period_date}/{last_period_date}.json'

        r = get_fitbit_metrics(self.fitbit_user_id, data)

        if r['status'] == 'fail':
            logger.error(f'pull_secondary_time_series error: {r["message"]}')            
            return {"status" : r['status'], "message" : r["message"]}
        
        result = r['result']
        
        session_player_periods = []
        for index, p in enumerate(self.session_player_periods_b.all()):
            p.fitbit_steps = result["fitbit_steps"]["result"]["activities-tracker-steps"][index]["value"]
            p.fitbit_calories = result["fitbit_calories"]["result"]["activities-tracker-calories"][index]["value"]

            p.fitbit_minutes_sedentary = result["fitbit_minutes_sedentary"]["result"]["activities-tracker-minutesSedentary"][index]["value"]
            p.fitbit_minutes_lightly_active = result["fitbit_minutes_lightly_active"]["result"]["activities-tracker-minutesLightlyActive"][index]["value"]
            p.fitbit_minutes_fairly_active = result["fitbit_minutes_fairly_active"]["result"]["activities-tracker-minutesFairlyActive"][index]["value"]
            p.fitbit_minutes_very_active = result["fitbit_minutes_very_active"]["result"]["activities-tracker-minutesVeryActive"][index]["value"]        

            session_player_periods.append(p)
        
        main.models.SessionPlayerPeriod.objects.bulk_update(session_player_periods, ['fitbit_steps', 
                                                                                     'fitbit_calories', 
                                                                                     'fitbit_minutes_sedentary', 
                                                                                     'fitbit_minutes_lightly_active',
                                                                                     'fitbit_minutes_fairly_active',
                                                                                     'fitbit_minutes_very_active'])

       
        

        return {"status" : "success"}

    def pull_fitbit_last_synced(self):
        '''
        pull the last time a fitbit has been synced
        '''

        logger = logging.getLogger(__name__) 

        data = {'devices' : f'https://api.fitbit.com/1/user/-/devices.json'}
        r = get_fitbit_metrics(self.fitbit_user_id, data)

        if r["status"]=="success":
            return self.process_fitbit_last_synced(r["result"]["devices"]["result"])
        else:
            return {"status" : "fail", "message" : r["message"]}

    def calcs_for_payblock(self, session_player_period=None):
        '''
        calc averages and payments for pay block
        '''

        if not session_player_period:
            session_player_period = self.get_todays_session_player_period()

        if not session_player_period:
            return

        parameter_set_pay_block = session_player_period.get_pay_block()

        self.calc_averages_for_block(parameter_set_pay_block)
        self.calc_payments_for_block(parameter_set_pay_block)

        return {"value" : "success", "message" : ""}

    def calc_averages_for_block(self, parameter_set_pay_block):
        '''
        calc player periods averages for a specified time block
        '''

        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=parameter_set_pay_block)

        for i in session_player_periods:
            i.calc_and_store_average_zone_minutes()
    
    def calc_payments_for_block(self, parameter_set_pay_block):
        '''
        calc player payments for a specified time block
        '''

        session_player_periods = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=parameter_set_pay_block)

        for i in session_player_periods:
            i.calc_and_store_payment()

    def process_fitbit_last_synced(self, r):
        '''
        process result of pulling fitbit last sync time
        '''

        logger = logging.getLogger(__name__) 

        devices = r

        v = -1
            
        try:
            v = devices[0].get("lastSyncTime",-1)                
        except Exception  as e: 
            logger.info(e)
            return {"status" : "fail", "message" : "no devices found"}

        if v == -1:                   
            return {"status" : "fail", "message" : "last sync error"}
        else:
            a=[]
            
            for i in devices:

                v = datetime.strptime(i.get("lastSyncTime"),'%Y-%m-%dT%H:%M:%S.%f')

                #test synced today
                #v = v-timedelta(days=1)

                #logger.info(f'pull_fitbit_last_synced sync: time {v}')

                d = {}
                d["last_sync"] = todays_date()
                d["last_sync"] = d["last_sync"].replace(hour=v.hour,minute=v.minute, second=v.second,microsecond=v.microsecond,
                                                        year=v.year,month=v.month,day=v.day)

                #logger.info(f'pull_fitbit_last_synced sync time: {d}')

                d["device"] = i.get("deviceVersion")

                a.append(d)
            
            sorted(a, key = lambda i: i['last_sync'], reverse=True)

            self.fitbit_last_synced = a[0]['last_sync'] #datetime.strptime(v,'%Y-%m-%dT%H:%M:%S.%f')
            self.fitbit_device = a[0]['device']
            self.save()

            #logger.info(f"pull_fitbit_last_synced sync time: { self.fitbit_last_synced}")

            return {"status" : "success", "message" : ""}

    def get_fitbit_last_sync_str(self):

        if not self.fitbit_last_synced:
            return "---"

        prm = main.models.Parameters.objects.first()
        tmz = pytz.timezone(prm.experiment_time_zone) 

        return  self.fitbit_last_synced.astimezone(tmz).strftime("%-m/%#d/%Y %#-I:%M %p")
    
    def fitbit_synced_today(self):
        '''
        true if the subject has synced their fitbit today
        '''
        logger = logging.getLogger(__name__) 
        d_today = todays_date().date()

        if not self.fitbit_last_synced:
            return False
        
        prm = main.models.Parameters.objects.first()
        tmz = pytz.timezone(prm.experiment_time_zone)

        d_fitbit=self.fitbit_last_synced.astimezone(tmz).date()

        #logger.info(f'fitbitSyncedToday {self} Today:{d_today} Last Synced:{d_fitbit}')

        if d_fitbit >= d_today:
            return True
        else:
            return False
    
    def fitbit_synced_last_30_min(self):
        '''
        true if the subject has synced their fitbit in the last 30 minutes
        '''
        logger = logging.getLogger(__name__)        

        if not self.fitbit_last_synced:
            return False
        
        prm = main.models.Parameters.objects.first()

        if datetime.now(pytz.UTC) - self.fitbit_last_synced <= timedelta(minutes=30):
            return True

        return False
    
    def get_current_survey_link(self):
        '''
        return, if any, the current survey link
        '''

        todays_session_player_period = self.get_todays_session_player_period()

        survey_link = ""

        if todays_session_player_period:
            survey_session_period = self.session_player_periods_b.filter(survey_complete=False,
                                                                         session_period__period_number__lte=todays_session_player_period.session_period.period_number).first()

            if survey_session_period:
                survey_link = survey_session_period.get_survey_link()
        
        return survey_link
    
    def get_current_missed_check_ins(self):
        '''
        return the number of missed check in up to now
        '''

        #session not started for before first period
        if not self.session.started or self.session.is_before_first_period():
            return 0
        
        #session is complete
        if self.session.is_after_last_period():
            return self.session_player_periods_b.filter(check_in=False).count()

        todays_session_player_period = self.get_todays_session_player_period()

        if not todays_session_player_period:
            return 0

        #session in progress
        return self.session_player_periods_b.filter(check_in=False, session_period__period_number__lt=todays_session_player_period.session_period.period_number).count()

    def get_help_doc(self, help_doc_title):
        '''
        return a processed help doc with help_doc_title
        '''
        help_doc_subject = self.session.parameter_set.help_doc_subject_set.help_docs_subject.all().filter(title=help_doc_title)

        if help_doc_subject:
            help_doc_json = help_doc_subject.first().json()
            help_doc_json["text"] = self.process_help_doc(help_doc_json["text"])
        else:
            help_doc_json = {"text" : "Not Found."}

        return help_doc_json
    
    def process_help_doc(self, text):
        '''
        take raw text and return processed version of it
        '''

        p = self.get_todays_session_player_period()

        wrist_time = format_minutes(p.session_period.parameter_set_period.minimum_wrist_minutes)

        text = text.replace('#Individual_Zone_Minutes#', self.individual_zone_mintutes_html())
        text = text.replace('#Group_Zone_Minutes#', self.group_zone_minutes_html())
        text = text.replace('#my_label#', self.parameter_set_player.label_html())
        text = text.replace('#wrist_time#', wrist_time)

        partner = self.session.session_players.filter(group_number=self.group_number).exclude(id=self.id).first()
        if partner:
            text = text.replace('#partner_label#', partner.parameter_set_player.label_html())

        if p:
            pay_block = p.get_pay_block()

            text = text.replace('#fixed_pay#', str(pay_block.fixed_pay))
            text = text.replace('#earn_fitbit_percent#', str(pay_block.no_pay_percent))

        return text

    def individual_zone_mintutes_html(self):
        '''
        return html table of individual zone minutes
        '''

        p = self.get_todays_session_player_period()

        if not p:
            return "Table not available"

        pay_block = p.get_pay_block()

        html = f"""<center><table class='table table-hover table-condensed table-responsive-md w-auto'>
                        <thead>
                            <th scope='col' class='text-center w-auto'>Average Zone Minutes</th>
                            <th scope='col' class='text-center w-auto'>Bonus Earnings</th>                            
                        </thead>
                        <tbody>"""

        for i in pay_block.parameter_set_pay_block_payments_a.all().order_by('-zone_minutes'):
                
            html = html + f"""<tr>
                             <td class='text-center w-auto'>{i.label}</td>
                             <td class='text-center w-auto'>${i.payment}</td>
                          </tr>"""
                
        html = html + """</tbody></table></center>"""
        

        return html
    
    def group_zone_minutes_html(self):
        '''
        return html table of individual zone minutes
        '''

        p = self.get_todays_session_player_period()

        if not p:
            return "Table not available"

        pay_block = p.get_pay_block()

        html = f"""<center><table class='table table-hover table-condensed table-responsive-md w-auto'>
                        <thead>
                            <th scope='col' class='text-center w-auto'>Average Zone Minutes</th>
                            <th scope='col' class='text-center w-auto'>Bonus Earning</th>                            
                        </thead>
                        <tbody>"""

        for i in pay_block.parameter_set_pay_block_payments_a.all().order_by('-zone_minutes'):
                
            html = html + f"""<tr>
                             <td class='text-center w-auto'>{i.label}</td>
                             <td class='text-center w-auto'>${i.group_bonus}</td>
                          </tr>"""
                
        html = html + """</tbody></table></center>"""
        

        return html

    def get_group_members(self):
        '''
        return other players in group
        '''

        return self.session.session_players.filter(group_number=self.group_number)

    def write_payblock_csv(self, pay_block, writer):
        '''
        take csv writer and add row
        '''
        # ["Session ID", "Payblock Number", "payblock type", "Player",  "Recruiter ID", "Group", "Total Zone Minutes"]

        values_list = []

        zone_minutes_list = self.session_player_periods_b.filter(session_period__parameter_set_period__parameter_set_pay_block=pay_block)

        for i in zone_minutes_list:
            if i.check_in:
                values_list.append(i.zone_minutes)
            else:
                 values_list.append(0)

        block_earnings = self.get_block_earnings(pay_block)

        writer.writerow([self.session.id, 
                        pay_block.pay_block_number,
                        pay_block.pay_block_type,
                        self.player_number,
                        self.recruiter_id_private,
                        self.group_number,
                        sum(values_list),
                        statistics.mean(values_list),
                        statistics.median(values_list),
                        block_earnings["fixed"],
                        block_earnings["individual"],
                        block_earnings["group_bonus"],
                        block_earnings["earnings_no_pay_percent"]])

    def json(self, get_chat=True):
        '''
        json object of model
        '''
        todays_session_player_period = self.get_todays_session_player_period()

        chat = []

        if self.session.parameter_set.enable_chat:
            chat = [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects.filter(session_player__in=self.session.session_players.all())
                                                                                        .filter(session_player__group_number=self.group_number)     
                                                                                .order_by('-timestamp')[:100:-1]
                    ]
        
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

            "disabled" : self.disabled,
            "consent_form_required" : self.consent_form_required,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            #"connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.json(),

            "chat" : chat,

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

            "earnings_fixed" : round(todays_session_player_period.get_fixed_pay()) if todays_session_player_period else None,
            "individual_earnings" : round(todays_session_player_period.earnings_individual) if todays_session_player_period else None,
            "group_earnings" : round(todays_session_player_period.earnings_group) if todays_session_player_period else False,
            "no_pay_percent" : todays_session_player_period.get_no_pay_percent() if todays_session_player_period else False,            

            "fitbit_last_synced" : self.get_fitbit_last_sync_str(),
            "fitbit_synced_last_30_min" : self.fitbit_synced_last_30_min(),
            "fitbit_user_id" : self.fitbit_user_id,

            "wrist_time_met_for_checkin" : todays_session_player_period.wrist_time_met() if todays_session_player_period else False,

            "todays_wrist_minutes" : todays_session_player_period.get_formated_wrist_minutes() if todays_session_player_period else "---",
            "todays_zone_minutes" :  todays_session_player_period.zone_minutes if todays_session_player_period else "---",
            "todays_average_zone_minutes" : todays_session_player_period.average_pay_block_zone_minutes if todays_session_player_period else "---",
            "groups_average_zone_minutes" : todays_session_player_period.get_team_average() if todays_session_player_period else "---",
            

            "survey_link" : self.get_current_survey_link(),
        }
    
    def json_for_staff(self):
        '''
        return json for staff screen
        '''

        chat = []

        if self.session.parameter_set.enable_chat:
            chat = [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects.filter(session_player__in=self.session.session_players.all())
                                                                                        .filter(session_player__group_number=self.group_number)     
                                                                                .order_by('-timestamp')[:100:-1]
                    ]

        todays_session_player_period = self.get_todays_session_player_period()  

        # if todays_session_player_period:
        #     period_number = todays_session_player_period.session_period.period_number
        # elif session. 

        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "group_number" : self.group_number,

            "player_number" : self.player_number,
            #"player_key" : self.player_key,

            "disabled" : self.disabled,
            "consent_form_required" : self.consent_form_required,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.json(),

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

            "chat" : chat,

            "session_player_periods" : [i.json_for_staff() for i in self.session_player_periods_b.select_related('session_period')],

            # "current_block_earnings" : self.get_current_block_earnings(),

            "checked_in_today" : todays_session_player_period.check_in if todays_session_player_period else None,
            #"group_checked_in_today" : todays_session_player_period.group_checked_in_today() if todays_session_player_period else False,
            "missed_check_ins" : self.get_current_missed_check_ins(),

            #"individual_earnings" : round(todays_session_player_period.get_individual_bonus_payment()) if todays_session_player_period else None,
            #"group_earnings" : round(todays_session_player_period.get_group_parameter_set_payment()) if todays_session_player_period else False,
            #"no_pay_percent" : todays_session_player_period.get_no_pay_percent if todays_session_player_period else False,

            "fitbit_last_synced" : self.get_fitbit_last_sync_str(),
            "fitbit_synced_last_30_min" : self.fitbit_synced_last_30_min(),
            "fitbit_user_id" : self.fitbit_user_id,

            "wrist_time_met_for_checkin" : todays_session_player_period.wrist_time_met() if todays_session_player_period else False,

            "todays_wrist_minutes" : todays_session_player_period.get_formated_wrist_minutes() if todays_session_player_period else "---",
            "todays_zone_minutes" :  todays_session_player_period.zone_minutes if todays_session_player_period else "---",

            #"survey_link" : self.get_current_survey_link(),
        }
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

        todays_session_player_period = self.get_todays_session_player_period()

        return{
            "id" : self.id,  

            "player_number" : self.player_number,
            "parameter_set_player" : self.parameter_set_player.json_for_subject(),
            "session_player_periods_1" : self.get_session_player_periods_1_json(),
            "session_player_periods_2" : self.get_session_player_periods_2_json(),
            "parameter_set_player" : self.parameter_set_player.json(),
            "current_block_earnings" : self.get_current_block_earnings(),
            "checked_in_today" : todays_session_player_period.check_in if todays_session_player_period else None,
            "group_checked_in_today" : todays_session_player_period.group_checked_in_today() if todays_session_player_period else False,
            "fitbit_last_synced" : self.get_fitbit_last_sync_str(),
            "fitbit_synced_last_30_min" : self.fitbit_synced_last_30_min(),
            "wrist_time_met_for_checkin" : todays_session_player_period.wrist_time_met() if todays_session_player_period else False,
        }

    def json_min(self):
        '''
        minimal json object of model
        '''

        todays_session_player_period = self.get_todays_session_player_period()

        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "group_number" : self.group_number,   
            "player_number" : self.player_number, 

            "parameter_set_player" : self.parameter_set_player.json(),

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "fitbit_last_synced" : self.get_fitbit_last_sync_str(),
            "fitbit_user_id" : self.fitbit_user_id,

            "checked_in_today" : todays_session_player_period.check_in if todays_session_player_period else None,
            "todays_wrist_minutes" : todays_session_player_period.get_formated_wrist_minutes() if todays_session_player_period else "---",
            "todays_zone_minutes" :  todays_session_player_period.zone_minutes if todays_session_player_period else "---",
        }


        