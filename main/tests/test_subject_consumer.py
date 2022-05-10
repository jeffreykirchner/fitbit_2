'''
build test
'''
from copy import deepcopy
from decimal import  Decimal

import logging
import sys

from django.test import TestCase

from main.globals import todays_date

from main.models import Session
from main.models import SessionPlayer

from main.consumers import take_get_session_subject
from main.consumers import take_check_in

from main.consumers import take_start_experiment
from main.consumers import take_update_session_form

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
        session_player_1 = self.session.session_players.get(player_number=1)
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

        session_player_1 = self.session.session_players.first()
        session = Session.objects.all().first()

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
        r = take_update_session_form(session.id, {'formData': [{'name': 'title', 'value': '*** New Session ***'}, {'name': 'start_date', 'value': d_today}]})
        self.assertEqual(r["value"], "success")
        session = Session.objects.all().first()

        r = take_start_experiment(session.id, {})
        self.assertEqual(r["value"], "success")
        self.assertEqual(r["started"], True)
        session = Session.objects.all().first()
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

        session_player_1 = self.session.session_players.first()
        self.assertEqual(session_player_1.session_player_periods_b.first().check_in, True)
        
        



