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

import main


class SessionPlayerPeriod(models.Model):
    '''
    session player period model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_periods_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_periods_b")

    earnings_individual = models.DecimalField(verbose_name='Individual Earnings', decimal_places=2, default=0, max_digits=5)     #earnings from individual activity this period
    earnings_group = models.DecimalField(verbose_name='Group Earnings', decimal_places=2, default=0, max_digits=5)               #earnings from group bonus this period
    earnings_no_pay_percent = models.IntegerField(verbose_name='No Pay Fitbit Percent', default=0)                               #no pay fitbit percent

    zone_minutes = models.IntegerField(verbose_name='Zone Minutes', default=0)        #todays heart active zone minutes
    #sleep_minutes = models.IntegerField(verbose_name='Sleep Minutes', default=0)      #todays minutes asleep

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
    fitbit_age = models.IntegerField(default=0)                        #age reported by fitbit.

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

        self.zone_minutes = random.randrange(0, 90)

        self.fitbit_on_wrist_minutes = random.randrange(max(self.session_period.parameter_set_period.minimum_wrist_minutes, 0), 1440)
        self.fitbit_heart_time_series = {"message":"filled with test data"}

        if random.randrange(1,10) == 1 or not self.wrist_time_met():
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
        
    def get_individual_parameter_set_payment(self):
        '''
        calc and return individual earnings
        '''
        # pervious_session_player_period = self.get_pervious_player_period()

        # if not pervious_session_player_period:
        #     return 0

        period_payment = self.session_period.parameter_set_period.get_payment(self.zone_minutes)

        if period_payment:
            return period_payment.payment

        return 0
    
    def get_individual_parameter_set_no_pay_percent(self):
        '''
        calc and return no pay percent
        '''
        # pervious_session_player_period = self.get_pervious_player_period()

        # if not pervious_session_player_period:
        #     return 0

        period_payment = self.session_period.parameter_set_period.get_payment(self.zone_minutes)

        if period_payment:
            return period_payment.no_pay_percent

        return 0
    
    def get_group_parameter_set_payment(self):
        '''
        calc and return individual earnings
        '''
        # pervious_session_player_period = self.get_pervious_player_period()

        # if not pervious_session_player_period:
        #     return 0

        period_payment = self.session_period.parameter_set_period.get_payment(self.get_lowest_group_zone_minutes())

        if period_payment:
            return period_payment.group_bonus

        return 0

    def calc_and_store_payment(self):
        '''
        calculate and store payment
        '''

        if not self.check_in:
            self.earnings_individual=0
            self.earnings_group=0
            self.earnings_no_pay_percent=0
            self.save()
            return {"value":"fail", "message" : "not checked in"}

        self.earnings_individual = self.get_individual_parameter_set_payment()
        self.earnings_no_pay_percent = self.get_individual_parameter_set_no_pay_percent()
        self.save()

        if self.group_checked_in_today():
            e = self.get_group_parameter_set_payment()
        else:
            e = 0

        g = main.models.SessionPlayerPeriod.objects.filter(session_period=self.session_period,
                                                           session_player__group_number=self.session_player.group_number)
        g.update(earnings_group=e)

        return {"value":"success", "message" : ""}
    
    def group_checked_in_today(self):
        '''
        return true if all group members have checked in
        '''

        no_checkin_count = self.session_period.session_player_periods_a.filter(session_player__group_number=self.session_player.group_number,
                                                                               check_in=False).count()

        if no_checkin_count > 0 :
            return False
        
        return True
    
    def get_lowest_group_zone_minutes(self):
        '''
        return the lowest zone minute total from a group member this period
        '''

        return self.session_period.session_player_periods_a.filter(session_player__group_number=self.session_player.group_number) \
                                                           .order_by('zone_minutes').first().zone_minutes

    def get_pervious_player_period(self):
        '''
        return the SessionPlayerPeriod that preceeded this one
        '''

        return self.session_player.session_player_periods_b.filter(session_period__period_number=self.session_period.period_number-1).first()

    def get_earning(self):
        '''
        get earnings from period
        '''

        return self.earnings_individual + self.earnings_group
    
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

    def pull_secondary_metrics(self, save_pull_time, result):
        '''
        pull extra metrics
        '''

        logger = logging.getLogger(__name__)

        if self.session_player.fitbit_user_id == "":
            return {"status" : "fail", "message" : "no fitbit user id"}
        
        # if self.fitbit_profile:
        #     logger.info(f"pull_secondary_metrics: Secondary metrics already pulled")
        #     return {"status" : "fail", "message" : "Secondary metrics already pulled"}

        # first_period_date = self.session_player.session.session_periods.first().period_date.strftime("%Y-%m-%d")
        # last_period_date = self.session_player.session.session_periods.last().period_date.strftime("%Y-%m-%d")

        temp_s = self.session_period.period_date.strftime("%Y-%m-%d")

        #test date
        #temp_s = "2021-1-25"

        #data = {}

        # if save_pull_time:
        #     data['devices'] = 'https://api.fitbit.com/1/user/-/devices.json'
        #     data["fitbit_profile"] = f'https://api.fitbit.com/1/user/-/profile.json'

        # data["fitbit_activities"] = f'https://api.fitbit.com/1/user/-/activities/list.json?afterDate={temp_s}&sort=asc&offset=0&limit=100'
        # data["fitbit_heart_time_series"] = f'https://api.fitbit.com/1/user/-/activities/heart/date/{temp_s}/1d.json'

        # r = get_fitbit_metrics(self.session_player.fitbit_user_id, data)

        # if r['status'] == 'fail':
        #     logger.error(f'pull_secondary_metrics error: {r["message"]}')            
        #     return {"status" : r['status'], "message" : r["message"]}

        # result = r['result']

        try: 
            if save_pull_time:    
                self.session_player.process_fitbit_last_synced(result["devices"]["result"])
                self.fitbit_profile = result["fitbit_profile"]["result"]
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

        # r = self.pull_secondary_metrics(save_pull_time)

        # if r["status"] == "success":
        with transaction.atomic():
            self.check_in = True
            self.save()

            self.calc_and_store_payment()
            
        return {"status" : "success"}
    
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
        #                  "Checked In", "Checked In Forced", "Individual Earnings", "Group Earnings", "Total Earnings", "Last Visit Time"])                    "Checked In", "Checked In Forced", "Individual Earnings", "Group Earnings", "Total Earnings", "Last Visit Time"]

        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.group_number,
                         self.zone_minutes,
                         #self.sleep_minutes,
                         self.fitbit_minutes_heart_peak,
                         self.fitbit_minutes_heart_cardio,
                         self.fitbit_minutes_heart_fat_burn,
                         self.fitbit_minutes_heart_out_of_range,
                         self.fitbit_min_heart_rate_zone_bpm,
                         self.fitbit_resting_heart_rate,
                         self.fitbit_age,
                         self.fitbit_on_wrist_minutes,
                         self.check_in,
                         self.check_in_forced,
                         self.earnings_individual,
                         self.earnings_group,
                         self.get_earning(),
                         self.earnings_no_pay_percent,
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
             self.session_player.group_number]

        if self.fitbit_heart_time_series:
            time_dict = {}

            for i in self.fitbit_heart_time_series["activities-heart-intraday"]["dataset"]:
                time_dict[i["time"]] = i["value"] 

            for i in range(1440):
                v.append(time_dict.get(str(timedelta(minutes=i)), ""))
        
        writer.writerow(v)
    
    def write_activities_download_csv(self, writer):
        '''
        take csv writer and add row
        '''
    #    ["Session ID", "Period", "Player", "Group", "Activity", "Zone Minutes", "Start Time", "End Time"]
       

        if self.fitbit_activities:

            for a in self.fitbit_activities["activities"]:
                v = [self.session_period.session.id,
                        self.session_period.period_number,
                        self.session_player.player_number,
                        self.session_player.group_number]
                
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
            "earnings_individual" : round(self.earnings_individual),
            "earnings_group" : round(self.earnings_group),
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

            "earnings_individual" : round(self.earnings_individual),
            "earnings_group" : round(self.earnings_group),
            "earnings_total" : self.get_earning(),
            "earnings_no_pay_percent" : self.earnings_no_pay_percent,
            "zone_minutes" : self.zone_minutes,
            "fitbit_on_wrist_minutes" : self.fitbit_on_wrist_minutes,
            "last_login" : self.last_login,
            "check_in" : self.check_in,
            "period_type" : self.session_period.parameter_set_period.period_type,
            "pay_block" : self.session_period.parameter_set_period.pay_block,
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

            "earnings_individual" : round(self.earnings_individual),
            "earnings_group" : round(self.earnings_group),
            "earnings_total" : self.get_earning(),
            "earnings_no_pay_percent" : self.earnings_no_pay_percent,
            "zone_minutes" : self.zone_minutes,
            "fitbit_on_wrist_minutes" : self.get_formated_wrist_minutes(),
            "fitbit_min_heart_rate_zone_bpm" : self.fitbit_min_heart_rate_zone_bpm,
            "fitbit_resting_heart_rate" : self.fitbit_resting_heart_rate,
            "fitbit_age" : self.fitbit_age,    
            "last_login" : self.last_login,
            "check_in" : self.check_in,
            "check_in_forced" : self.check_in_forced,
            "period_type" : self.session_period.parameter_set_period.period_type,
            "pay_block" : self.session_period.parameter_set_period.pay_block,
            "wrist_time_met" : self.wrist_time_met(),
            "survey_complete" : self.survey_complete,           

        }