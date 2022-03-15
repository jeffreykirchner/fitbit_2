'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class ChatTypes(models.TextChoices):
    '''
    chat types
    '''
    ALL = 'All', _('All')
    INDIVIDUAL = 'Individual', _('Individual')

class ExperimentPhase(models.TextChoices):
    '''
    experiment phases
    '''
    INSTRUCTIONS = 'Instructions', _('Instructions')
    RUN = 'Run', _('Run')
    DONE = 'Done', _('Done')

class PeriodType(models.TextChoices):
    '''
    period types
    '''
    NO_PAY = 'No Pay', _('No Pay')
    FIXED_PAY = 'Fixed Pay', _('Fixed Pay')
    INDIVIDUAL_PAY = 'Individual Pay', _('Individual Pay')
    GROUP_PAY = 'Group Pay', _('Group Pay')
