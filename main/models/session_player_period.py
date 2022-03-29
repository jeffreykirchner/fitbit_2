'''
session player period results
'''

#import logging
import random

from django.db import models

from main.models import SessionPlayer
from main.models import SessionPeriod


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

    fitbit_birthday = models.CharField(max_length = 100, default = '')  #todays fitbit listed birthday
    fitbit_weight = models.DecimalField(decimal_places=2, default=0, max_digits=6)                      #todays fitbit listed weight
    fitbit_height = models.DecimalField(decimal_places=2, default=0, max_digits=6)                      #todays fitbit listed height

    #charge 4 active zone minutes
    fitbit_minutes_heart_out_of_range = models.IntegerField(default=0)         #todays heart rate out of range
    fitbit_minutes_heart_fat_burn = models.IntegerField(default=0)             #todays heart rate lightly fat burn
    fitbit_minutes_heart_cardio = models.IntegerField(default=0)               #todays heart rate cardio
    fitbit_minutes_heart_peak = models.IntegerField(default=0)                 #todays heart rate peak

    fitbit_heart_time_series = models.CharField(max_length = 100000, default = '')  #today's heart rate time series
    fitbit_sleep_time_series = models.CharField(max_length = 100000, default = '')  #today's sleep time series

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

    
    def calc_and_store_payment(self):
        '''
        calculate and store payment
        '''

        if not self.check_in:
            return {"status":"fail", "message" : "not checked in"}

        pervious_session_player_period = self.get_pervious_player_period()
        if not pervious_session_player_period:
            return {"status":"fail", "message" : "this is the first period"}

        paramter_set_period_payment = self.session_period.parameter_set_period.get_payment(pervious_session_player_period.zone_minutes)

        if paramter_set_period_payment:
            self.earnings_individual = paramter_set_period_payment.payment
        
        paramter_set_period_payment = self.session_period.parameter_set_period.get_payment(pervious_session_player_period.get_lowest_group_zone_minutes())
        
        if paramter_set_period_payment:
            self.earnings_group = paramter_set_period_payment.group_bonus

        self.save()

        return {"status":"success", "message" : ""}
    
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
        }