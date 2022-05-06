'''
build test
'''
from copy import deepcopy
from decimal import  Decimal

import logging
import sys

from django.test import TestCase

from main.models import Session
from main.models import SessionPlayer

from main.consumers import take_get_session_subject

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

        r = take_get_session_subject(session_player_1.id, data)
        self.assertEqual(r["show_fitbit_connect"], False)
        self.assertEqual(r["fitbit_error_message"], "")

    def test_check_in(self):
        '''
        test subject check in from consumer
        '''

        session_player_1 = self.session.sesion_players.first()


        



