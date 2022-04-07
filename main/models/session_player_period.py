'''
session player period results
'''

#import logging
import random

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from main.models import SessionPlayer
from main.models import SessionPeriod

from main.globals import get_fitbit_metrics
from main.globals import format_minutes


class SessionPlayerPeriod(models.Model):
    '''
    session player period model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_periods_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_periods_b")

    earnings_individual = models.DecimalField(verbose_name='Individual Earnings', decimal_places=2, default=0, max_digits=5)        #earnings from individual activity this period
    earnings_group = models.DecimalField(verbose_name='Individual Earnings', decimal_places=2, default=0, max_digits=5)             #earnings from group bonus this period

    zone_minutes = models.IntegerField(verbose_name='Zone Minutes', default=0)        #todays heart active zone minutes
    sleep_minutes = models.IntegerField(verbose_name='Sleep Minutes', default=0)      #todays minutes asleep

    check_in = models.BooleanField(verbose_name='Checked In', default=False)          #true if player was able to check in this period

    #fitbit metrics
    #charge 3 metrics depriciated
    fitbit_minutes_sedentary = models.IntegerField(default=0)         #todays tracker sedentary minutes
    fitbit_minutes_lightly_active = models.IntegerField(default=0)    #todays tracker lightly active minutes
    fitbit_minutes_fairly_active = models.IntegerField(default=0)     #todays tracker fairly active minutes
    fitbit_minutes_very_active = models.IntegerField(default=0)       #todays tracker very active minutes

    fitbit_steps = models.IntegerField(default=0)                     #todays tracker steps
    fitbit_calories = models.IntegerField(default=0)                  #todays tracker calories

    fitbit_birthday = models.CharField(max_length=100, default='')  #todays fitbit listed birthday
    fitbit_weight = models.DecimalField(decimal_places=2, default=0, max_digits=6)                      #todays fitbit listed weight
    fitbit_height = models.DecimalField(decimal_places=2, default=0, max_digits=6)                      #todays fitbit listed height

    #charge 4 active zone minutes
    fitbit_minutes_heart_out_of_range = models.IntegerField(default=0)         #todays heart rate out of range
    fitbit_minutes_heart_fat_burn = models.IntegerField(default=0)             #todays heart rate lightly fat burn
    fitbit_minutes_heart_cardio = models.IntegerField(default=0)               #todays heart rate cardio
    fitbit_minutes_heart_peak = models.IntegerField(default=0)                 #todays heart rate peak

    fitbit_heart_time_series = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)  #today's heart rate time series
    fitbit_sleep_time_series = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)  #today's sleep time series

    fitbit_on_wrist_minutes = models.IntegerField(default=0)         #minutes fit bit was one wrist (sum of heart time series) 
    fitbit_min_heart_rate_zone_bpm = models.IntegerField(default=0)  #minimum bmp a subject must have to register active zone minutes

    last_login = models.DateTimeField(null=True, blank=True)          #first time the subject logged in this day 

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.session_player.parameter_set_player.id_label}, Period {self.session_period.period_number}"

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
        
        if random.randrange(1,10) == 1:
            self.check_in = False
        else:
            self.check_in = True

        self.save()

    
    def get_individual_parameter_set_payment(self):
        '''
        calc and return individual earnings
        '''
        pervious_session_player_period = self.get_pervious_player_period()

        if not pervious_session_player_period:
            return 0

        period_payment = self.session_period.parameter_set_period.get_payment(pervious_session_player_period.zone_minutes)

        if period_payment:
            return period_payment.payment

        return 0
    
    def get_group_parameter_set_payment(self):
        '''
        calc and return individual earnings
        '''
        pervious_session_player_period = self.get_pervious_player_period()

        if not pervious_session_player_period:
            return 0

        period_payment = self.session_period.parameter_set_period.get_payment(pervious_session_player_period.get_lowest_group_zone_minutes())

        if period_payment:
            return period_payment.group_bonus

        return 0

    def calc_and_store_payment(self):
        '''
        calculate and store payment
        '''

        if not self.check_in:
            self.parameter_set_period_payment=0
            self.earnings_group=0
            self.save()
            return {"status":"fail", "message" : "not checked in"}

        self.earnings_individual = self.get_individual_parameter_set_payment()

        if self.group_checked_in_today():
            self.earnings_group = self.get_group_parameter_set_payment()

        self.save()

        return {"status":"success", "message" : ""}
    
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
            return {"status" : "fail", "message" : "No fitbit user id"}

        temp_s = self.session_period.period_date.strftime("%Y-%m-%d")
        #temp_s = "today"
        #temp_s="2020-11-20"
        # 
        
        data = {'fitbit_heart_time_series' : f'https://api.fitbit.com/1/user/-/activities/heart/date/{temp_s}/1d.json'}

        result = get_fitbit_metrics(self.session_player.fitbit_user_id, data)

        if  result['fitbit_heart_time_series']['status'] == 'success':
            self.fitbit_heart_time_series = result['fitbit_heart_time_series']['result']                 

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

        return {"status" : result['fitbit_heart_time_series']['status'], 
                "message" : result['fitbit_heart_time_series']['message']}

    def write_summary_download_csv(self, writer):
        '''
        take csv writer and add row
        '''
        writer.writerow([self.session_period.session.id,
                         self.session_period.period_number,
                         self.session_player.player_number,
                         self.session_player.parameter_set_player.id_label,
                         self.earnings,])
        
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            
            "period_number" : self.session_period.period_number,

            "earnings_individual" : self.earnings_individual,
            "earnings_group" : self.earnings_group,
            "earnings_total" : self.get_earning(),
            "zone_minutes" : self.zone_minutes,
            "fitbit_on_wrist_minutes" : self.fitbit_on_wrist_minutes,
            "last_login" : self.last_login,
            "check_in" : self.check_in,
            "period_type" : self.session_period.parameter_set_period.period_type,
            "pay_block" : self.session_period.parameter_set_period.pay_block,
        }