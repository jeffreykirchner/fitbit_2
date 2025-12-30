'''
session player period results
'''

#import logging
from datetime import datetime
from datetime import timedelta
import math
import random
import logging
import uuid
import pytz

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.conf import settings

from main.models import SessionPlayer
from main.models import SessionPeriod
from main.models import Parameters

from main.globals import get_fitbit_metrics
from main.globals import format_minutes
from main.globals import PayBlockType
from main.globals import format_timedelta

import main


class SessionPlayerPeriod(models.Model):
    '''
    session player period model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_periods_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_periods_b")

    earnings_fixed = models.DecimalField(verbose_name='Fixed Pay Earnings', decimal_places=2, default=0, max_digits=5)           #earnings from fixed pay activity this period
    earnings_no_pay_percent = models.IntegerField(verbose_name='No Pay Fitbit Percent', default=0)                               #no pay fitbit percent

    earnings_individual = models.DecimalField(verbose_name='Individual Earnings', decimal_places=2, default=0, max_digits=5)     #earnings from individual activity this period
    earnings_group = models.DecimalField(verbose_name='Group Earnings', decimal_places=2, default=0, max_digits=5)               #earnings from group bonus this period
    
    zone_minutes = models.IntegerField(verbose_name='Zone Minutes', default=0)        #todays heart active zone minutes
    #sleep_minutes = models.IntegerField(verbose_name='Sleep Minutes', default=0)      #todays minutes asleep
    average_pay_block_zone_minutes = models.DecimalField(verbose_name='Average Zone Minutes', decimal_places=2, default=0, max_digits=6)

    current_group_number = models.IntegerField(null=True, blank=True, verbose_name="Group Number this Period")  #store group number at time of period

    check_in = models.BooleanField(verbose_name='Checked In', default=False)                     #true if player was able to check in this period
    check_in_forced = models.BooleanField(verbose_name='Checked In Forced', default=False)       #true if staff forces a check in
    back_pull = models.BooleanField(verbose_name='Back Pull', default=False)                     #true if session period data was pulled the next day to fill in missing time

    survey_complete = models.BooleanField(verbose_name='Survey Complete', default=True)          #true if player has completed the survey for this period.
    activity_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Subject Activity Key')

    #fitbit metrics
    #charge 3 metrics depriciated
    fitbit_minutes_sedentary = models.IntegerField(default=0)         #todays tracker sedentary minutes
    fitbit_minutes_lightly_active = models.IntegerField(default=0)    #todays tracker lightly active minutes
    fitbit_minutes_fairly_active = models.IntegerField(default=0)     #todays tracker fairly active minutes
    fitbit_minutes_very_active = models.IntegerField(default=0)       #todays tracker very active minutes

    fitbit_steps = models.IntegerField(default=0)                     #todays tracker steps
    fitbit_calories = models.IntegerField(default=0)                  #todays tracker calories

    fitbit_profile = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)     #todays fitbit profile
    fitbit_activities = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)  #todays fitbit profile

    #charge 4 active zone minutes
    fitbit_minutes_heart_out_of_range = models.IntegerField(default=0)         #todays heart rate out of range
    fitbit_minutes_heart_fat_burn = models.IntegerField(default=0)             #todays heart rate lightly fat burn
    fitbit_minutes_heart_cardio = models.IntegerField(default=0)               #todays heart rate cardio
    fitbit_minutes_heart_peak = models.IntegerField(default=0)                 #todays heart rate peak

    fitbit_heart_time_series = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)  #today's heart rate time series
    #fitbit_sleep_time_series = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)  #today's sleep time series

    fitbit_on_wrist_minutes = models.IntegerField(default=0)          #minutes fit bit was one wrist (sum of heart time series) 
    fitbit_min_heart_rate_zone_bpm = models.IntegerField(default=0)   #minimum bmp a subject must have to register active zone minutes
    fitbit_resting_heart_rate = models.IntegerField(default=0)        #resting heart rate
    fitbit_age = models.IntegerField(default=0)                       #age reported by fitbit.

    last_login = models.DateTimeField(null=True, blank=True)          #last time the subject logged this day
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Period {self.session_period.period_number}, Date {self.session_period.period_date}"

    class Meta:
        
        verbose_name = 'Session Player Period'
        verbose_name_plural = 'Session Player Periods'
        ordering = ['session_player__session', 'session_player', 'session_period__period_number']
        constraints = [
            models.UniqueConstraint(fields=['session_player', 'session_period'], name='unique_session_player_period'),
        ]
    
    def fill_with_test_data(self):
        '''
        fill with test data
        '''
        
        self.zone_minutes = random.randrange(0, self.session_player.session.parameter_set.graph_y_max+10)
        
        self.fitbit_on_wrist_minutes = random.randrange(max(self.session_period.parameter_set_period.minimum_wrist_minutes, 0), 1440)
        self.fitbit_heart_time_series = {"message":"filled with test data"}

        if random.randrange(1,10) <= 2 or not self.wrist_time_met():
            self.check_in = False
        else:
            self.check_in = True

        self.save()
        
    def wrist_time_met(self):
        '''
        return true if subject has required wrist yesterday for todays payment
        '''

        if self.fitbit_on_wrist_minutes >= self.session_period.parameter_set_period.minimum_wrist_minutes:
            return True
        
        return False

    def get_expected_fitbit_min_heart_rate_zone_bpm(self):
        '''
        return the expect fitbit_min_heart_rate_zone_bpm based on age and resting HR
        '''

        #return 12

        if self.fitbit_age == 0:
            return None
        
        if self.fitbit_resting_heart_rate == 0:
            return None

        max_heart_rate = 220 - self.fitbit_age
        heart_rate_reserve = max_heart_rate - self.fitbit_resting_heart_rate

        return math.floor(self.fitbit_resting_heart_rate + 0.4 * heart_rate_reserve)

    def get_fitbit_min_heart_rate_zone_bpm_flag(self):
        '''
        return true if incorrect AZM calc
        '''

        if self.fitbit_age >= self.session_player.parameter_set_player.parameter_set.age_warning:
            return True

        fitbit_min_heart_rate_zone_bpm_expected = self.get_expected_fitbit_min_heart_rate_zone_bpm()
        v = False

        if fitbit_min_heart_rate_zone_bpm_expected:
            if self.fitbit_min_heart_rate_zone_bpm != fitbit_min_heart_rate_zone_bpm_expected:
                v = True
        
        return v

    def get_pay_block(self):
        '''
        return parameter set pay block for this period
        '''

        return self.session_period.parameter_set_period.parameter_set_pay_block
        
    def get_individual_bonus_payment(self):
        '''
        calc and return individual bonus payment
        '''

        pay_block_type = self.get_pay_block().pay_block_type

        if pay_block_type == PayBlockType.BLOCK_PAY_GROUP or \
           pay_block_type == PayBlockType.BLOCK_PAY_INDIVIDUAL or \
           pay_block_type == PayBlockType.BLOCK_PAY_COMPETITION: 

            block_payment = self.session_period.parameter_set_period.get_payment(self.average_pay_block_zone_minutes)

            if block_payment:
                return block_payment.payment

        return 0
    
    def get_group_bonus_payment(self):
        '''
        calc and return group bonus payment
        '''

        pay_block_type = self.get_pay_block().pay_block_type

        if pay_block_type == PayBlockType.BLOCK_PAY_GROUP:
            #pull the lowest average zone minutes from the group and pay everyone that amount
            zone_minutes = self.get_lowest_group_average_zone_minutes()

            block_payment = self.session_period.parameter_set_period.get_payment(zone_minutes)

            if block_payment:
                return block_payment.group_bonus
        elif pay_block_type == PayBlockType.BLOCK_PAY_COMPETITION:
            #if this player has the highest average zone minutes in the group, pay the group bonus
            group_members = self.session_player.get_group_members()
            highest_avg = -1
            is_highest = True

            for i in group_members:
                # i.calc_averages_for_block(self.get_pay_block())
                session_player_period = i.session_player_periods_b.get(session_period=self.session_period)

                if session_player_period.average_pay_block_zone_minutes > highest_avg:
                    highest_avg = session_player_period.average_pay_block_zone_minutes
                    if i != self.session_player:
                        is_highest = False
                    else:
                        is_highest = True

            if is_highest:
                block_payment = self.session_period.parameter_set_period.get_payment(self.average_pay_block_zone_minutes)

                if block_payment:
                    return block_payment.group_bonus

        return 0

    def get_fixed_pay(self):
        '''
        calc and return no pay percent
        '''

        return self.get_pay_block().fixed_pay
    
    def get_no_pay_percent(self):
        '''
        calc and return no pay percent
        '''

        return self.get_pay_block().no_pay_percent

    def calc_and_store_payment(self):
        '''
        calculate and store payment
        '''

        self.earnings_individual = self.get_individual_bonus_payment()
        self.earnings_group = self.get_group_bonus_payment()

        if not self.check_in:
            self.earnings_fixed=0
            self.earnings_no_pay_percent=0
            self.save()
            return {"value":"fail", "message" : "not checked in"}

        self.earnings_fixed = self.get_fixed_pay()
        self.earnings_no_pay_percent = self.get_no_pay_percent()

        self.save()

        return {"value":"success", "message" : ""}
    
    def calc_and_store_payment_group(self):
        '''
        calculate and store payments for all group memebers this period 
        '''
        session_player_periods = main.models.SessionPlayerPeriod.objects.filter(session_period=self.session_period) \
                                                             .filter(session_player__group_number=self.session_player.group_number)

        for i in session_player_periods:
            i.calc_and_store_payment()

    def calc_and_store_average_zone_minutes(self):
        '''
        calc and store the average zone minutes up to this point in the pay block
        '''

        zone_minutes_list = self.session_player \
                                .session_player_periods_b \
                                .filter(session_period__parameter_set_period__parameter_set_pay_block=self.get_pay_block()) \
                                .filter(check_in=True) \
                                .filter(session_period__period_number__lte=self.session_period.period_number) \
                                .values_list('zone_minutes', flat=True)
        
        zone_minutes_list = list(zone_minutes_list)

        block_period_count = self.session_player \
                                 .session_player_periods_b \
                                 .filter(session_period__parameter_set_period__parameter_set_pay_block=self.get_pay_block()) \
                                 .filter(session_period__period_number__lte=self.session_period.period_number) \
                                 .count()

        if block_period_count > 0:
            self.average_pay_block_zone_minutes = sum(zone_minutes_list) / block_period_count
        else:
            self.average_pay_block_zone_minutes = 0

        self.save()

    def group_checked_in_today(self):
        '''
        return true if all group members have checked in
        '''

        no_checkin_count = self.session_period.session_player_periods_a.filter(session_player__group_number=self.session_player.group_number,
                                                                               check_in=False).count()

        if no_checkin_count > 0 :
            return False
        
        return True
    
    def get_lowest_group_average_zone_minutes(self):
        '''
        return the lowest aerage zone minute total from this day
        '''
        
        return self.session_period.session_player_periods_a.filter(session_player__group_number=self.session_player.group_number) \
                                                           .filter(session_period=self.session_period) \
                                                           .order_by('average_pay_block_zone_minutes').first().average_pay_block_zone_minutes   
                                                                              
    def get_earning(self):
        '''
        get earnings from period
        '''

        return self.earnings_fixed
    
    def get_formated_wrist_minutes(self):
        '''
        return wrist minutes string
        '''
        return format_minutes(self.fitbit_on_wrist_minutes)

    def pull_fitbit_heart_time_series(self):
        '''
        pull heart rate time series from fitbit
        '''

        if self.session_player.fitbit_user_id == "":
            return {"status" : "fail", "message" : "no fitbit user id"}

        temp_s = self.session_period.get_fitbit_formatted_date()
        #temp_s = "today"
        #temp_s="2020-11-20"
        # 
        
        data = {'fitbit_heart_time_series' : f'https://api.fitbit.com/1/user/-/activities/heart/date/{temp_s}/1d.json'}

        r = get_fitbit_metrics(self.session_player.fitbit_user_id, data)

        if  r['status'] == 'success':
            self.process_fitbit_heart_time_series(r['result']['fitbit_heart_time_series']['result'])
            
            return {"status" : r['result']['fitbit_heart_time_series']['status'], 
                    "message" : r['result']['fitbit_heart_time_series']['message']}
        else:
            return {"status" : "fail", 
                    "message" : r['message']}
    
    def process_fitbit_heart_time_series(self, d):
        '''
        process fitbit heartrate time series d
        '''

        self.fitbit_heart_time_series = d         
        self.fitbit_resting_heart_rate = self.fitbit_heart_time_series['activities-heart'][0]['value'].get('restingHeartRate', 0)

        heart_summary = self.fitbit_heart_time_series['activities-heart'][0]['value']['heartRateZones']

        #store heart rate ranges
        for i in range(4):
        
            minutes = heart_summary[i].get("minutes",0)
            name =  heart_summary[i].get("name","not found")

            #logger.info(f'pullFibitBitHeartRate {name} {minutes}')

            if name == 'Out of Range':
                self.fitbit_minutes_heart_out_of_range = minutes
            elif name == 'Fat Burn':
                self.fitbit_minutes_heart_fat_burn = minutes
                self.fitbit_min_heart_rate_zone_bpm =  heart_summary[i].get("min",0)
            elif name == 'Cardio':
                self.fitbit_minutes_heart_cardio = minutes
            elif name == 'Peak':
                self.fitbit_minutes_heart_peak = minutes
        
        v = self.fitbit_heart_time_series.get("activities-heart-intraday",-1)

        if v == -1:
            self.fitbit_on_wrist_minutes = 0
        else:
            v = v.get('dataset',-1)
            
        if v==-1:
            self.fitbit_on_wrist_minutes = 0
        else:
            self.fitbit_on_wrist_minutes = len(v)

            #active zone minutes, new calculation                
            self.zone_minutes = self.fitbit_minutes_heart_cardio * 2 + \
                                self.fitbit_minutes_heart_peak * 2 + \
                                self.fitbit_minutes_heart_fat_burn

        self.save()

    def take_heart_rate_from_date_range(self, heart_rate_dict):
        '''
        take and store heart rate from date range dict.
        '''

        self.fitbit_heart_time_series = heart_rate_dict

        heart_rate_zones = self.fitbit_heart_time_series["value"]["heartRateZones"]
                
        for i in heart_rate_zones:
            
            minutes = i.get("minutes", 0)
            name =  i.get("name", "not found")

            #logger.info(f'pullFibitBitHeartRate {name} {minutes}')

            if name == 'Out of Range':
                self.fitbit_minutes_heart_out_of_range = minutes
            elif name == 'Fat Burn':
                self.fitbit_minutes_heart_fat_burn = minutes
                self.fitbit_min_heart_rate_zone_bpm =  i.get("min", 0)
            elif name == 'Cardio':
                self.fitbit_minutes_heart_cardio = minutes
            elif name == 'Peak':
                self.fitbit_minutes_heart_peak = minutes

        self.save()

    def process_metrics(self, save_pull_time, result):
        '''
        process metrics
        '''

        logger = logging.getLogger(__name__)

        if self.session_player.fitbit_user_id == "":
            return {"status" : "fail", "message" : "no fitbit user id"}
        

        temp_s = self.session_period.period_date.strftime("%Y-%m-%d")

        try: 
            if save_pull_time:    
                self.fitbit_profile = result["fitbit_profile"]["result"]
                self.session_player.process_fitbit_last_synced(result["devices"]["result"], self.fitbit_profile['user']['timezone'])
                self.fitbit_age = self.fitbit_profile['user']['age']

            self.fitbit_heart_time_series = result["fitbit_heart_time_series"]["result"]
            self.process_fitbit_heart_time_series(self.fitbit_heart_time_series)

            #only store activities for this day
            fitbit_activities_raw = result["fitbit_activities"]["result"]
            
            self.fitbit_activities = {"activities" : []}
            for i in fitbit_activities_raw["activities"]:
                if temp_s in i["startTime"]:
                    self.fitbit_activities["activities"].append(i)           

            #store pull time           
            if save_pull_time:
                self.last_login = datetime.now()

            self.save()
            
        except KeyError as e:
            logger.error(f"pull_secondary_metrics error: {e}")
            
        return {"status" : "success", "message" :""}

    def take_check_in(self, save_pull_time):
        '''
        check subject in for this period
        '''

        self.check_in = True
        self.save()

        self.calc_and_store_average_zone_minutes()
        self.calc_and_store_payment()
        
        return {"status" : "success"}
    
    def get_team_average(self, exclude_self=True):
        '''
        return the team's average AZM up to this point in the pay block
        '''

        group_members = self.session_player.get_group_members()

        if group_members.count() == 2:

            for i in group_members:
                if i != self.session_player:
                    i.calc_averages_for_block(self.get_pay_block())
                    session_player_period = i.session_player_periods_b.get(session_period=self.session_period)

                    return session_player_period.average_pay_block_zone_minutes

        return None

    def get_survey_link(self):
        '''
        get survey link
        '''

        if self.survey_complete:
            return ""
        
        p = Parameters.objects.first()

        #https://chapmanu.co1.qualtrics.com/jfe/form/SV_9BJPiWNYT9hZ6tM?student_id=[student%20id]&session_id=10786&first_name=[first%20name]&last_name=[last%20name]&email=[email]&recruiter_id=[recruiter%20id]
        link_string = f'{self.session_period.parameter_set_period.survey_link}?'
        link_string += f'session_id={self.session_player.session.id}&'
        link_string += f'player_id={self.session_player.player_number}&'
        link_string += f'recruiter_id_public={self.session_player.recruiter_id_public}&'
        link_string += f'recruiter_id_private={self.session_player.recruiter_id_private}&'
        link_string += f'period={self.session_period.period_number}&'
        link_string += f'activity_key={self.activity_key}&'
        link_string += f'session_name={self.session_period.session.title}&'
        link_string += f'return_link={p.site_url}&'
        

        return link_string

    def get_last_login_str(self):

        if not self.last_login:
            return ""

        prm = main.models.Parameters.objects.first()
        tmz = pytz.timezone(prm.experiment_time_zone) 

        return  self.last_login.astimezone(tmz).strftime("%m/%d/%Y %I:%M:%S %p") 

    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''
        # ["Session ID", "Period", "Player", "Group", 
        #                  "Zone Minutes", "Sleep Minutes", "Peak Minutes", "Cardio Minutes", "Fat Burn Minutes", "Out of Range Minutes", "Zone Minutes HR BPM", "Resting HR", "Age", "Wrist Time", 
        #                  "Checked In", "Checked In Forced", "fixed pay", "Individual Earnings", "Group Earnings", "Total Earnings", "Last Visit Time"])                    "Checked In", "Checked In Forced", "Individual Earnings", "Group Earnings", "Total Earnings", "Last Visit Time"]

        earnings_individual = 0
        earnings_group = 0
        earnings_total = 0
        no_pay_total = 0

        pay_block = self.get_pay_block()

        if self.session_period.is_last_period_in_block:
            v = self.session_player.get_block_earnings(pay_block)
            earnings_individual = v["individual"]
            earnings_group = v["group_bonus"]
            earnings_total = v["total"]
            no_pay_total = v["earnings_no_pay_percent"]

        writer.writerow([self.session_period.session.id,
                         pay_block.pay_block_type,
                         pay_block.pay_block_number,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.note,
                         self.session_player.recruiter_id_private,
                         self.session_player.parameter_set_player.id_label,
                         self.session_player.group_number if not self.current_group_number else self.current_group_number,
                         self.session_player.fitbit_device,
                         self.zone_minutes,
                         self.average_pay_block_zone_minutes,
                         #self.sleep_minutes,
                         self.fitbit_minutes_heart_peak,
                         self.fitbit_minutes_heart_cardio,
                         self.fitbit_minutes_heart_fat_burn,
                         self.fitbit_minutes_heart_out_of_range,
                         self.fitbit_min_heart_rate_zone_bpm,
                         self.get_expected_fitbit_min_heart_rate_zone_bpm(),
                         self.fitbit_resting_heart_rate,
                         self.fitbit_age,
                         self.fitbit_on_wrist_minutes,
                         self.check_in,
                         self.check_in_forced,
                         self.earnings_fixed,
                         earnings_individual,
                         earnings_group,
                         earnings_total,
                         self.earnings_no_pay_percent,
                         no_pay_total,
                         self.get_last_login_str(),
                         self.fitbit_calories,
                         self.fitbit_steps,
                         self.fitbit_minutes_sedentary,
                         self.fitbit_minutes_lightly_active,
                         self.fitbit_minutes_fairly_active,
                         self.fitbit_minutes_very_active,
                         ])
    
    def write_heart_rate_download_csv(self, writer):
        '''
        take csv writer and add row
        '''
        v = [self.session_period.session.id,
             self.session_period.period_number,
             self.session_player.player_number,
             self.session_player.note,
             self.session_player.recruiter_id_private,
             self.session_player.group_number if not self.current_group_number else self.current_group_number,]

        if self.fitbit_heart_time_series:
            time_dict = {}

            if self.fitbit_heart_time_series.get("activities-heart-intraday", False):
                for i in self.fitbit_heart_time_series["activities-heart-intraday"]["dataset"]:
                    time_dict[i["time"]] = i["value"] 

            for i in range(1440):
                v.append(time_dict.get(format_timedelta(timedelta(minutes=i)), ""))
        
        writer.writerow(v)
    
    def write_activities_download_csv(self, writer):
        '''
        take csv writer and add row
        '''
    #    ["Session ID", "Period", "Player", "Recruiter id", "Group", "Activity", "Zone Minutes", "Start Time", "End Time"]
       

        if self.fitbit_activities:

            for a in self.fitbit_activities["activities"]:
                v = [self.session_period.session.id,
                        self.session_period.period_number,
                        self.session_player.player_number,
                        self.session_player.note,
                        self.session_player.recruiter_id_private,
                        self.session_player.group_number if not self.current_group_number else self.current_group_number]
                
                v.append(a["activityName"])

                #zone minutes
                zone_minutes = 0

                if a.get("activeZoneMinutes", False):
                    zone_minutes = a["activeZoneMinutes"].get("totalMinutes", 0)

                v.append(zone_minutes)

                #start/end time
                start_time = datetime.strptime(a.get("startTime"),'%Y-%m-%dT%H:%M:%S.%f%z')
                end_time = start_time + timedelta(milliseconds=a.get("duration"))

                prm = main.models.Parameters.objects.first()
                tmz = pytz.timezone(prm.experiment_time_zone) 

                v.append(start_time.astimezone(tmz).strftime("%#m/%#d/%Y %#I:%M %p"))
                v.append(end_time.astimezone(tmz).strftime("%#m/%#d/%Y %#I:%M %p"))

                #log type
                v.append(a.get("logType"))

                writer.writerow(v)

    def json_for_check_in(self):
        '''
        json object after check in 
        '''

        return{
            "earnings_individual" : round(self.earnings_individual,2),
            "earnings_group" : round(self.earnings_group,2),
            "earnings_total" : self.get_earning(),
            "check_in" : self.check_in,
            "group_checked_in_today" : self.group_checked_in_today(),  
        }

    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            
            "period_number" : self.session_period.period_number,
            "period_day_of_week" : self.session_period.get_formatted_day_of_week(),

            "earnings_fixed" : round(self.earnings_fixed,2),
            "earnings_individual" : round(self.earnings_individual,2),
            "earnings_group" : round(self.earnings_group,2),
            "earnings_total" : round(self.get_earning(),2),
            "earnings_no_pay_percent" : self.earnings_no_pay_percent,

            "zone_minutes" : self.zone_minutes,
            "average_pay_block_zone_minutes" : round(self.average_pay_block_zone_minutes, 1),
            "fitbit_on_wrist_minutes" : self.fitbit_on_wrist_minutes,
            "last_login" : self.last_login,
            "check_in" : self.check_in,
            "period_type" : self.session_period.parameter_set_period.parameter_set_pay_block.pay_block_type,
            "wrist_time_met" : self.wrist_time_met(),
            "survey_complete" : self.survey_complete,           
        }
    
    def json_for_staff(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            
            "period_number" : self.session_period.period_number,
            "fitbit_formatted_date" : self.session_period.get_formatted_date(),

            "earnings_fixed" : round(self.earnings_fixed,2),
            "earnings_individual" : round(self.earnings_individual,2) if self.session_period.is_last_period_in_block else 0,
            "earnings_group" : round(self.earnings_group,2) if self.session_period.is_last_period_in_block else 0,
            "earnings_total" : round(self.get_earning(),2),
            "earnings_no_pay_percent" : self.earnings_no_pay_percent,
            
            "zone_minutes" : self.zone_minutes,
            "average_pay_block_zone_minutes" : self.average_pay_block_zone_minutes,
            "fitbit_on_wrist_minutes" : self.get_formated_wrist_minutes(),
            "fitbit_min_heart_rate_zone_bpm" : self.fitbit_min_heart_rate_zone_bpm,
            "fitbit_min_heart_rate_zone_bpm_expected" : self.get_expected_fitbit_min_heart_rate_zone_bpm(),
            "fitbit_min_heart_rate_zone_bpm_flag" : self.get_fitbit_min_heart_rate_zone_bpm_flag(),
            "fitbit_resting_heart_rate" : self.fitbit_resting_heart_rate,

            "fitbit_age" : self.fitbit_age,    
            "last_login" : self.last_login,
            "check_in" : self.check_in,
            "check_in_forced" : self.check_in_forced,
            "period_type" : self.session_period.parameter_set_period.parameter_set_pay_block.pay_block_type,
            "pay_block_number" : self.session_period.parameter_set_period.parameter_set_pay_block.pay_block_number,
            "wrist_time_met" : self.wrist_time_met(),
            "survey_complete" : self.survey_complete,           
        }