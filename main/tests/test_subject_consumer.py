'''
build test
'''
from copy import deepcopy
from decimal import  Decimal

import logging

from django.test import TestCase

import main

class TestSubjectConsumer(TestCase):
    fixtures = ['auth_user.json', 'main.json']

    user = None

    def setUp(self):
        logger = logging.getLogger(__name__)
