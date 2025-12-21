'''
gloabal functions related to parameter sets
'''

from django.db import models
from django.utils.translation import gettext_lazy as _

import main

class ExperimentPhase(models.TextChoices):
    '''
    experiment phases
    '''
    INSTRUCTIONS = 'Instructions', _('Instructions')
    RUN = 'Run', _('Run')
    DONE = 'Done', _('Done')

class PayBlockType(models.TextChoices):
    '''
    pay block types
    '''
    FIXED_PAY_ONLY = 'Fixed Pay Only', _('Fixed Pay Only')
    BLOCK_PAY_GROUP = 'Block Pay Group', _('Block Pay Group')
    BLOCK_PAY_INDIVIDUAL = 'Block Pay Individual', _('Block Pay Individual')
    EARN_FITBIT = 'Earn Fitbit', _('Earn Fitbit')
    BLOCK_PAY_COMPETITION = 'Block Pay Competition', _('Block Pay Competition')

class GroupAssignmentType(models.TextChoices):
    '''
    group assignment types
    '''
    INDIVIDUAL = 'Individual', _('Individual')
    FIXED = 'Fixed', _('Fixed')
    SORTED = 'Sorted', _('Sorted')

class ColorAssignmentType(models.TextChoices):
    '''
    color assignment types
    '''
    FIXED = 'Fixed', _('Fixed')
    DYNAMIC = 'Dynamic', _('Dynamic')

