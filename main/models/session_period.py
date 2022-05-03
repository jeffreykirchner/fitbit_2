'''
session period model
'''

#import logging

from django.db import models
from django.utils.timezone import now

from main.models import Session
from main.models import  ParameterSetPeriod

import main

class SessionPeriod(models.Model):
    '''
    session period model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_periods")
    parameter_set_period = models.ForeignKey(ParameterSetPeriod, on_delete=models.CASCADE, related_name="session_periods_b", blank=True, null=True)
 
    period_number = models.IntegerField()                        #period number from 1 to N
    period_date = models.DateField(default=now)                  #date of period

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"Session {self.session.title}, Periods {self.period_number}, Date {self.period_date}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'period_number'], name='unique_SD')
        ]
        verbose_name = 'Session Period'
        verbose_name_plural = 'Session Periods'
        ordering = ['period_number']
    
    def get_formatted_date(self):
        '''
        return formatted day of week
        '''

        return self.period_date.strftime("%#m/%#d/%Y")
    
    def get_formatted_day_of_week(self):
        '''
        return formatted day of week
        '''

        return self.period_date.strftime("%a")
    
    def get_formatted_day_of_week_full(self):
        '''
        return formatted day of week
        '''

        return self.period_date.strftime("%A")

    def get_fitbit_formatted_date(self):
        '''
        return period date in a fitbit formatted string
        '''

        return self.period_date.strftime("%Y-%m-%d")
        
    def json(self):
        '''
        json object of model
        '''
        #current_best_bid = self.get_current_best_bid()
        #current_best_offer = self.get_current_best_offer()

        #current_trade = self.get_current_trade()

        return{
            "id" : self.id,
            "period_number" : self.period_number,
            "period_date" : self.get_formatted_date(),
            "period_day_of_week" : self.get_formatted_day_of_week()
        }