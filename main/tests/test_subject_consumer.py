'''
build test
'''
from datetime import  datetime
from datetime import  timedelta
from copy import deepcopy
from decimal import  Decimal

import logging
import sys
from unicodedata import decimal

from django.test import TestCase

from main.globals import todays_date

from main.models import Session
from main.models import SessionPlayer

from main.consumers import take_get_session_subject
from main.consumers import take_check_in

from main.consumers import take_start_experiment
from main.consumers import take_update_session_form
from main.consumers import take_help_doc_subject

import main

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None
    session = None
    session_player_1 = None

    def setUp(self):
        sys._called_from_test = True
        logger = logging.getLogger(__name__)

        self.session = Session.objects.all().first()
    
    def test_get_session_subject(self):
        '''
        test get session subject from consumer
        '''
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_1 = session.session_players.get(player_number=1)
        data = {'playerKey': '2ce05dfc-c421-4c04-ae35-4b2cf4166978', 'first_load_done': False}

        #no fitbit connection
        r = take_get_session_subject(session_player_1.id, data)
        self.assertEqual(r["show_fitbit_connect"], True)
        self.assertEqual(r["fitbit_error_message"], "Connect your fitbit the app.")

        session_player_1.fitbit_user_id = "abc123"
        session_player_1.save()
        data2 = {'playerKey': '2ce05dfc-c421-4c04-ae35-4b2cf4166978', 'first_load_done': True}

        #success
        r = take_get_session_subject(session_player_1.id, data)
        self.assertEqual(r["show_fitbit_connect"], False)
        self.assertEqual(r["fitbit_error_message"], "")

    def test_check_in(self):
        '''
        test subject check in from consumer
        '''

        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_1 = session.session_players.first()
       
        session_player_1.fitbit_user_id = "abc123"
        session_player_1.save()

        data = {'playerKey': '2ce05dfc-c421-4c04-ae35-4b2cf4166978', 'first_load_done': False}

        data1 = {"software_version":"1.00", "current_period" : 1}
        data2 = {"software_version":"1.01", "current_period" : 1}
        data3 = {"software_version":"1.00", "current_period" : 2}

        #session not found
        r = take_check_in(session.id+1, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "Session not available.")
        
        #software version
        r = take_check_in(session.id, session_player_1.id, data2)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "Refresh your browser.")

        #current period
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "Session has not begun.")

        #start experiment
        d_today = todays_date().date()
        r = take_update_session_form(session.id, {'formData': {'title': session.title, 'start_date': d_today}})
        self.assertEqual(r["value"], "success")
        session = Session.objects.get(title='70 Period Group Pay For Tests')

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        self.assertEqual(session.get_current_session_period().period_number, 1)

        #period number
        r = take_check_in(session.id, session_player_1.id, data3)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], " Refresh your browser.")

        #survey
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "  Refresh your browser.")

        #complete survey
        session_periods_first =  session_player_1.session_player_periods_b.first()
        session_periods_first.survey_complete = True
        session_periods_first.save()

        #session finished
        session.finished = True
        session.save()
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "Session complete.")
        session.finished = False
        session.save()

        #subject disabled
        session_player_1.disabled = True
        session_player_1.save()
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], " Session complete.")
        session_player_1.disabled = False
        session_player_1.save()

        #wrist time
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "You have not worn your Fitbit long enough today.")
        session_periods_first.fitbit_on_wrist_minutes = 1440
        session_periods_first.save()

        #fitbit phone sync
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "fail")
        self.assertEqual(r["result"]["error_message"], "Sync your Fitbit to your phone.")

        #pull metrics
        r = take_get_session_subject(session_player_1.id, data)
        self.assertEqual(r["show_fitbit_connect"], False)
        self.assertEqual(r["fitbit_error_message"], "")

        #success
        r = take_check_in(session.id, session_player_1.id, data1)
        self.assertEqual(r["value"], "success")

        session_player_1 = session.session_players.first()
        self.assertEqual(session_player_1.session_player_periods_b.first().check_in, True)
    
    def test_pay_level_fixed_pay(self):
        '''
        test correct pay at differnt zone minute levels
        '''

        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_3 = session.session_players.get(player_number=3)
        session_player_4 = session.session_players.get(player_number=4)

        #start experiment
        d_today = todays_date().date()
        r = take_update_session_form(session.id, {'formData': {'title': session.title, 'start_date': d_today}})
        self.assertEqual(r["value"], "success")
        session = Session.objects.get(title='70 Period Group Pay For Tests')

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        self.assertEqual(session.get_current_session_period().period_number, 1)

        #player 3
        session_player_3_p1 = session_player_3.session_player_periods_b.get(session_period__period_number=1)
        session_player_3_p1.check_in=True
        session_player_3_p1.zone_minutes=15
        session_player_3_p1.save()
        r=session_player_3.calcs_for_payblock(session_player_3_p1)
        self.assertEqual(r["value"], "success")

        session_player_3_p1 = session_player_3.session_player_periods_b.get(session_period__period_number=1)
        self.assertEqual(session_player_3_p1.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_3_p1.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_3_p1.earnings_group, Decimal('0'))
        self.assertEqual(session_player_3_p1.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_3_p1.average_pay_block_zone_minutes,  Decimal('15'))

        #player4
        session_player_4_p1 = session_player_4.session_player_periods_b.get(session_period__period_number=1)
        self.assertEqual(session_player_4_p1.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_group, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_4_p1.average_pay_block_zone_minutes,  Decimal('0'))

        #no check in
        session_player_4_p1.check_in=False
        session_player_4_p1.zone_minutes=45
        session_player_4_p1.save()

        r=session_player_4.calcs_for_payblock(session_player_4_p1)
        self.assertEqual(r["value"], "success")

        session_player_4_p1 = session_player_4.session_player_periods_b.get(session_period__period_number=1)
        self.assertEqual(session_player_4_p1.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_group, Decimal('0'))
        self.assertEqual(session_player_4_p1.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_4_p1.average_pay_block_zone_minutes,  Decimal('0'))

        #check block earnings
        session_player_3_p4 = session_player_3.session_player_periods_b.get(session_period__period_number=4)
        session_player_3_p4.check_in=True
        session_player_3_p4.zone_minutes=75
        session_player_3_p4.save()
        r=session_player_3.calcs_for_payblock(session_player_3_p4)
        self.assertEqual(r["value"], "success")

        session_player_4_p4 = session_player_4.session_player_periods_b.get(session_period__period_number=6)
        session_player_4_p4.check_in=True
        session_player_4_p4.zone_minutes=18
        session_player_4_p4.save()
        r=session_player_4.calcs_for_payblock(session_player_4_p4)
        self.assertEqual(r["value"], "success")

        session_player_4_p8 = session_player_4.session_player_periods_b.get(session_period__period_number=8)
        session_player_4_p8.check_in=True
        session_player_4_p8.zone_minutes=1
        session_player_4_p8.save()
        r=session_player_4.calcs_for_payblock(session_player_4_p8)
        self.assertEqual(r["value"], "success")

        self.assertEqual(session_player_3.get_block_earnings(1),{"fixed":6, "individual":0,"group_bonus":0,"total":6,"earnings_no_pay_percent":0})
        self.assertEqual(session_player_4.get_block_earnings(1),{"fixed":6, "individual":0,"group_bonus":0,"total":6,"earnings_no_pay_percent":0})
        
    def test_pay_level_group_pay(self):
        '''
        test correct pay at different zone minute levels
        '''

        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_5 = session.session_players.get(player_number=5)
        session_player_6 = session.session_players.get(player_number=6)

        d_today = (todays_date() - timedelta(days=15)).date()
        r = take_update_session_form(session.id, {'formData': {'title': session.title, 'start_date': d_today}})
        self.assertEqual(r["value"], "success")
        session = Session.objects.get(title='70 Period Group Pay For Tests')

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        self.assertEqual(session.get_current_session_period().period_number, 16)

        #player 5
        #zone minutes under 30 min
        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=15)
        session_player_5_p15.check_in=True
        session_player_5_p15.zone_minutes=15
        session_player_5_p15.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p15)
        self.assertEqual(r["value"], "success")

        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=15)
        self.assertEqual(session_player_5_p15.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p15.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p15.average_pay_block_zone_minutes,  Decimal('15'))

        #30 -44 min
        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=16)
        session_player_5_p16.check_in=True
        session_player_5_p16.zone_minutes=35
        session_player_5_p16.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p16)
        self.assertEqual(r["value"], "success")

        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=16)
        self.assertEqual(session_player_5_p16.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p16.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p16.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p16.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p16.average_pay_block_zone_minutes,  Decimal('25'))

        #45-59
        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=17)
        session_player_5_p17.check_in=True
        session_player_5_p17.zone_minutes=45
        session_player_5_p17.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p17)
        self.assertEqual(r["value"], "success")

        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=17)
        self.assertEqual(session_player_5_p17.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p17.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_5_p17.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p17.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p17.average_pay_block_zone_minutes,  Decimal('31.67'))

        #60+
        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=18)
        session_player_5_p18.check_in=False
        session_player_5_p18.zone_minutes=60
        session_player_5_p18.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p18)
        self.assertEqual(r["value"], "success")

        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=18)
        self.assertEqual(session_player_5_p18.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_5_p18.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p18.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p18.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p18.average_pay_block_zone_minutes,  Decimal('23.75'))

        #player 6
        session_player_6_p15 = session_player_6.session_player_periods_b.get(session_period__period_number=15)
        session_player_6_p15.check_in=True
        session_player_6_p15.zone_minutes=29
        session_player_6_p15.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p15)
        self.assertEqual(r["value"], "success")

        session_player_6_p15 = session_player_6.session_player_periods_b.get(session_period__period_number=15)
        self.assertEqual(session_player_6_p15.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p15.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_6_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_6_p15.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p15.average_pay_block_zone_minutes,  Decimal('29'))

        #30 -44 min
        session_player_6_p16 = session_player_6.session_player_periods_b.get(session_period__period_number=16)
        session_player_6_p16.check_in=True
        session_player_6_p16.zone_minutes=44
        session_player_6_p16.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p16)
        self.assertEqual(r["value"], "success")

        session_player_6_p16 = session_player_6.session_player_periods_b.get(session_period__period_number=16)
        self.assertEqual(session_player_6_p16.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p16.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p16.earnings_group, Decimal('15'))
        self.assertEqual(session_player_6_p16.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p16.average_pay_block_zone_minutes,  Decimal('36.5'))
        
        #45-59
        session_player_6_p17 = session_player_6.session_player_periods_b.get(session_period__period_number=17)
        session_player_6_p17.check_in=True
        session_player_6_p17.zone_minutes=59
        session_player_6_p17.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p17)
        self.assertEqual(r["value"], "success")

        session_player_6_p17 = session_player_6.session_player_periods_b.get(session_period__period_number=17)
        self.assertEqual(session_player_6_p17.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p17.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p17.earnings_group, Decimal('23'))
        self.assertEqual(session_player_6_p17.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p17.average_pay_block_zone_minutes,  Decimal('44'))

        #30 -44 min
        session_player_6_p18 = session_player_6.session_player_periods_b.get(session_period__period_number=18)
        session_player_6_p18.check_in=True
        session_player_6_p18.zone_minutes=31
        session_player_6_p18.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p18)
        self.assertEqual(r["value"], "success")

        session_player_6_p18 = session_player_6.session_player_periods_b.get(session_period__period_number=18)
        self.assertEqual(session_player_6_p18.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p18.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p18.earnings_group, Decimal('15'))
        self.assertEqual(session_player_6_p18.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p18.average_pay_block_zone_minutes,  Decimal('40.75'))

        #check player 5
        r=session_player_5.calcs_for_payblock(session_player_5_p15)

        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=15)
        self.assertEqual(session_player_5_p15.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_no_pay_percent, 0)

        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=16)
        self.assertEqual(session_player_5_p16.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p16.earnings_group, Decimal('15'))
        self.assertEqual(session_player_5_p16.earnings_no_pay_percent, 0)

        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=17)
        self.assertEqual(session_player_5_p17.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_5_p17.earnings_group, Decimal('23'))
        self.assertEqual(session_player_5_p17.earnings_no_pay_percent, 0)

        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=18)
        self.assertEqual(session_player_5_p18.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p18.earnings_group, Decimal('15'))
        self.assertEqual(session_player_5_p18.earnings_no_pay_percent, 0)

        #check earnings block
        session_player_5_p19 = session_player_5.session_player_periods_b.get(session_period__period_number=19)
        session_player_5_p19.check_in=True
        session_player_5_p19.zone_minutes=285
        session_player_5_p19.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p19)
        
        session_player_6_p19 = session_player_6.session_player_periods_b.get(session_period__period_number=19)
        session_player_6_p19.check_in=True
        session_player_6_p19.zone_minutes=200
        session_player_6_p19.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p19)

        r=session_player_5.calcs_for_payblock(session_player_5_p19)
        r=session_player_6.calcs_for_payblock(session_player_6_p19)

        self.assertEqual(session_player_5.get_block_earnings(2),{"fixed":12, "individual":45,"group_bonus":15,"total":72,"earnings_no_pay_percent":0})
        self.assertEqual(session_player_6.get_block_earnings(2),{"fixed":15, "individual":30,"group_bonus":15,"total":60,"earnings_no_pay_percent":0})
    
    def test_pay_level_indvidual_pay(self):
        '''
        test correct pay at different zone minute levels
        '''
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_5 = session.session_players.get(player_number=5)
        session_player_6 = session.session_players.get(player_number=6)

        d_today = (todays_date() - timedelta(days=15)).date()
        r = take_update_session_form(session.id, {'formData': {'title': session.title, 'start_date': d_today}})
        self.assertEqual(r["value"], "success")
        session = Session.objects.get(title='70 Period Group Pay For Tests')

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        self.assertEqual(session.get_current_session_period().period_number, 16)

        #player 5
        #zone minutes under 30 min
        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=29)
        session_player_5_p15.check_in=True
        session_player_5_p15.zone_minutes=15
        session_player_5_p15.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p15)
        self.assertEqual(r["value"], "success")

        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=29)
        self.assertEqual(session_player_5_p15.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p15.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p15.average_pay_block_zone_minutes,  Decimal('15'))

        #30 -44 min
        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=30)
        session_player_5_p16.check_in=True
        session_player_5_p16.zone_minutes=35
        session_player_5_p16.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p16)
        self.assertEqual(r["value"], "success")

        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=30)
        self.assertEqual(session_player_5_p16.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p16.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p16.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p16.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p16.average_pay_block_zone_minutes,  Decimal('25'))

        #45-59
        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=31)
        session_player_5_p17.check_in=True
        session_player_5_p17.zone_minutes=45
        session_player_5_p17.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p17)
        self.assertEqual(r["value"], "success")

        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=31)
        self.assertEqual(session_player_5_p17.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_5_p17.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_5_p17.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p17.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p17.average_pay_block_zone_minutes,  Decimal('31.67'))

        #60+
        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=32)
        session_player_5_p18.check_in=False
        session_player_5_p18.zone_minutes=60
        session_player_5_p18.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p18)
        self.assertEqual(r["value"], "success")

        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=32)
        self.assertEqual(session_player_5_p18.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_5_p18.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p18.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p18.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_5_p18.average_pay_block_zone_minutes,  Decimal('23.75'))

        #player 6
        session_player_6_p15 = session_player_6.session_player_periods_b.get(session_period__period_number=29)
        session_player_6_p15.check_in=True
        session_player_6_p15.zone_minutes=29
        session_player_6_p15.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p15)
        self.assertEqual(r["value"], "success")

        session_player_6_p15 = session_player_6.session_player_periods_b.get(session_period__period_number=29)
        self.assertEqual(session_player_6_p15.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p15.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_6_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_6_p15.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p15.average_pay_block_zone_minutes,  Decimal('29'))

        #30 -44 min
        session_player_6_p16 = session_player_6.session_player_periods_b.get(session_period__period_number=30)
        session_player_6_p16.check_in=True
        session_player_6_p16.zone_minutes=44
        session_player_6_p16.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p16)
        self.assertEqual(r["value"], "success")

        session_player_6_p16 = session_player_6.session_player_periods_b.get(session_period__period_number=30)
        self.assertEqual(session_player_6_p16.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p16.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p16.earnings_group, Decimal('0'))
        self.assertEqual(session_player_6_p16.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p16.average_pay_block_zone_minutes,  Decimal('36.5'))
        
        #45-59
        session_player_6_p17 = session_player_6.session_player_periods_b.get(session_period__period_number=31)
        session_player_6_p17.check_in=True
        session_player_6_p17.zone_minutes=59
        session_player_6_p17.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p17)
        self.assertEqual(r["value"], "success")

        session_player_6_p17 = session_player_6.session_player_periods_b.get(session_period__period_number=31)
        self.assertEqual(session_player_6_p17.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p17.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p17.earnings_group, Decimal('0'))
        self.assertEqual(session_player_6_p17.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p17.average_pay_block_zone_minutes,  Decimal('44'))

        #30 -44 min
        session_player_6_p18 = session_player_6.session_player_periods_b.get(session_period__period_number=32)
        session_player_6_p18.check_in=True
        session_player_6_p18.zone_minutes=31
        session_player_6_p18.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p18)
        self.assertEqual(r["value"], "success")

        session_player_6_p18 = session_player_6.session_player_periods_b.get(session_period__period_number=32)
        self.assertEqual(session_player_6_p18.earnings_fixed, Decimal('3'))
        self.assertEqual(session_player_6_p18.earnings_individual, Decimal('60'))
        self.assertEqual(session_player_6_p18.earnings_group, Decimal('0'))
        self.assertEqual(session_player_6_p18.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_6_p18.average_pay_block_zone_minutes,  Decimal('40.75'))

        #check player 5
        r=session_player_5.calcs_for_payblock(session_player_5_p15)

        session_player_5_p15 = session_player_5.session_player_periods_b.get(session_period__period_number=29)
        self.assertEqual(session_player_5_p15.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p15.earnings_no_pay_percent, 0)

        session_player_5_p16 = session_player_5.session_player_periods_b.get(session_period__period_number=30)
        self.assertEqual(session_player_5_p16.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p16.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p16.earnings_no_pay_percent, 0)

        session_player_5_p17 = session_player_5.session_player_periods_b.get(session_period__period_number=31)
        self.assertEqual(session_player_5_p17.earnings_individual, Decimal('45'))
        self.assertEqual(session_player_5_p17.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p17.earnings_no_pay_percent, 0)

        session_player_5_p18 = session_player_5.session_player_periods_b.get(session_period__period_number=32)
        self.assertEqual(session_player_5_p18.earnings_individual, Decimal('30'))
        self.assertEqual(session_player_5_p18.earnings_group, Decimal('0'))
        self.assertEqual(session_player_5_p18.earnings_no_pay_percent, 0)

        #check earnings block
        session_player_5_p33 = session_player_5.session_player_periods_b.get(session_period__period_number=33)
        session_player_5_p33.check_in=True
        session_player_5_p33.zone_minutes=285
        session_player_5_p33.save()
        r=session_player_5.calcs_for_payblock(session_player_5_p33)

        session_player_6_p33 = session_player_6.session_player_periods_b.get(session_period__period_number=33)
        session_player_6_p33.check_in=True
        session_player_6_p33.zone_minutes=200
        session_player_6_p33.save()
        r=session_player_6.calcs_for_payblock(session_player_6_p33)

        self.assertEqual(session_player_5.get_block_earnings(3),{"fixed":12, "individual":45,"group_bonus":0,"total":57,"earnings_no_pay_percent":0})
        self.assertEqual(session_player_6.get_block_earnings(3),{"fixed":15, "individual":30,"group_bonus":0,"total":45,"earnings_no_pay_percent":0})
    
    def test_pay_level_no_pay(self):
        '''
        test correct pay at differnt zone minute levels
        '''
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        session_player_7 = session.session_players.get(player_number=7)
        session_player_8 = session.session_players.get(player_number=8)

        d_today = (todays_date() - timedelta(days=85)).date()
        r = take_update_session_form(session.id, {'formData': {'title': session.title, 'start_date': d_today}})
        self.assertEqual(r["value"], "success")
        session = Session.objects.get(title='70 Period Group Pay For Tests')

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.get(title='70 Period Group Pay For Tests')
        self.assertEqual(session.get_current_session_period().period_number, 86)

        #player 7
        #zone minutes under 30 min
        session_player_7_p87 = session_player_7.session_player_periods_b.get(session_period__period_number=87)
        session_player_7_p87.check_in=True
        session_player_7_p87.zone_minutes=15
        session_player_7_p87.save()
        r=session_player_7.calcs_for_payblock(session_player_7_p87)
        self.assertEqual(r["value"], "success")

        session_player_7_p87 = session_player_7.session_player_periods_b.get(session_period__period_number=87)
        self.assertEqual(session_player_7_p87.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p87.average_pay_block_zone_minutes,  Decimal('5'))

        #30 -44 min
        session_player_7_p88 = session_player_7.session_player_periods_b.get(session_period__period_number=88)
        session_player_7_p88.check_in=True
        session_player_7_p88.zone_minutes=35
        session_player_7_p88.save()
        r=session_player_7.calcs_for_payblock(session_player_7_p88)
        self.assertEqual(r["value"], "success")

        session_player_7_p88 = session_player_7.session_player_periods_b.get(session_period__period_number=88)
        self.assertEqual(session_player_7_p88.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p88.average_pay_block_zone_minutes,  Decimal('12.5'))

        #45-59
        session_player_7_p89 = session_player_7.session_player_periods_b.get(session_period__period_number=89)
        session_player_7_p89.check_in=True
        session_player_7_p89.zone_minutes=45
        session_player_7_p89.save()
        r=session_player_7.calcs_for_payblock(session_player_7_p89)
        self.assertEqual(r["value"], "success")

        session_player_7_p89 = session_player_7.session_player_periods_b.get(session_period__period_number=89)
        self.assertEqual(session_player_7_p89.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p89.average_pay_block_zone_minutes,  Decimal('19'))

        #60+
        session_player_7_p90 = session_player_7.session_player_periods_b.get(session_period__period_number=90)
        session_player_7_p90.check_in=True
        session_player_7_p90.zone_minutes=60
        session_player_7_p90.save()
        r=session_player_7.calcs_for_payblock(session_player_7_p90)
        self.assertEqual(r["value"], "success")

        session_player_7_p90 = session_player_7.session_player_periods_b.get(session_period__period_number=90)
        self.assertEqual(session_player_7_p90.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p90.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p90.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p90.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p90.average_pay_block_zone_minutes,  Decimal('25.83'))


        #check player 8 still all zeros
        session_player_8_p85 = session_player_8.session_player_periods_b.get(session_period__period_number=85)

        r=session_player_8.calcs_for_payblock(session_player_8_p85)
        self.assertEqual(r["value"], "success")

        self.assertEqual(session_player_8_p85.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_group, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_no_pay_percent, 0)
        self.assertEqual(session_player_8_p85.average_pay_block_zone_minutes,  Decimal('0'))

        #player 8
        session_player_8_p85 = session_player_8.session_player_periods_b.get(session_period__period_number=85)
        session_player_8_p85.check_in=True
        session_player_8_p85.zone_minutes=29
        session_player_8_p85.save()
        r=session_player_8.calcs_for_payblock(session_player_8_p85)
        self.assertEqual(r["value"], "success")

        session_player_8_p85 = session_player_8.session_player_periods_b.get(session_period__period_number=85)
        self.assertEqual(session_player_8_p85.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_group, Decimal('0'))
        self.assertEqual(session_player_8_p85.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_8_p85.average_pay_block_zone_minutes,  Decimal('29'))

        #30 -44 min
        session_player_8_p86 = session_player_8.session_player_periods_b.get(session_period__period_number=86)
        session_player_8_p86.check_in=True
        session_player_8_p86.zone_minutes=44
        session_player_8_p86.save()
        r=session_player_8.calcs_for_payblock(session_player_8_p86)
        self.assertEqual(r["value"], "success")

        session_player_8_p86 = session_player_8.session_player_periods_b.get(session_period__period_number=86)
        self.assertEqual(session_player_8_p85.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_8_p86.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_8_p86.earnings_group, Decimal('0'))
        self.assertEqual(session_player_8_p86.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_8_p86.average_pay_block_zone_minutes,  Decimal('36.5'))
        
        #45-59
        session_player_8_p87 = session_player_8.session_player_periods_b.get(session_period__period_number=87)
        session_player_8_p87.check_in=True
        session_player_8_p87.zone_minutes=59
        session_player_8_p87.save()
        r=session_player_8.calcs_for_payblock(session_player_8_p87)
        self.assertEqual(r["value"], "success")

        session_player_8_p87 = session_player_8.session_player_periods_b.get(session_period__period_number=87)
        self.assertEqual(session_player_8_p85.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_8_p87.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_8_p87.earnings_group, Decimal('0'))
        self.assertEqual(session_player_8_p87.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_8_p87.average_pay_block_zone_minutes,  Decimal('44'))

        #re check player 7
        session_player_7_p87 = session_player_7.session_player_periods_b.get(session_period__period_number=87)
        self.assertEqual(session_player_7_p87.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p87.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p87.average_pay_block_zone_minutes,  Decimal('5'))

        session_player_7_p88 = session_player_7.session_player_periods_b.get(session_period__period_number=88)
        self.assertEqual(session_player_7_p88.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p88.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p88.average_pay_block_zone_minutes,  Decimal('12.5'))

        session_player_7_p89 = session_player_7.session_player_periods_b.get(session_period__period_number=89)
        self.assertEqual(session_player_7_p89.earnings_fixed, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_individual, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_group, Decimal('0'))
        self.assertEqual(session_player_7_p89.earnings_no_pay_percent, 8)
        self.assertEqual(session_player_7_p89.average_pay_block_zone_minutes,  Decimal('19'))

        #check earnings block
        self.assertEqual(session_player_7.get_block_earnings(7),{"fixed":0, "individual":0,"group_bonus":0,"total":0,"earnings_no_pay_percent":32})
        self.assertEqual(session_player_8.get_block_earnings(7),{"fixed":0, "individual":0,"group_bonus":0,"total":0,"earnings_no_pay_percent":24})
