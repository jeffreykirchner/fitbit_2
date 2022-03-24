'''
session player period results
'''

#import logging

from django.db import models

from main.models import SessionPlayer
from main.models import SessionPeriod


class SessionPlayerPeriod(models.Model):
    '''
    session player period model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_periods_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_periods_b")

    earnings_individual = models.IntegerField(verbose_name='Individual Earnings', default=0)        #earnings from individual activity this period
    earnings_group = models.IntegerField(verbose_name='Individual Earnings', default=0)             #earnings from group bonus this period

    zone_minutes = models.IntegerField(default=0)       #todays heart active zone minutes
    sleep_minutes = models.IntegerField(default=0)      #todays minutes asleep

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
            "zone_minutes" : self.zone_minutes,
            "fitbit_on_wrist_minutes" : self.fitbit_on_wrist_minutes,
            "last_login" : self.last_login,
        }