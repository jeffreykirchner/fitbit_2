'''
get todays tz adjusted info
'''
import pytz

from datetime import datetime

import main

#get todays, time zone adjusted date time object
def todays_date(time_zone=None):
    '''
        Get today's server time zone adjusted date time object with zeroed time
    '''
    #logger = logging.getLogger(__name__)
    #logger.info("Get todays date object")

    prm = main.models.Parameters.objects.first()

    if not time_zone:
        tmz = pytz.timezone(prm.experiment_time_zone)
    else:
        tmz = pytz.timezone(time_zone)

    d_today = datetime.now(tmz)
    d_today = d_today.replace(hour=0, minute=0, second=0, microsecond=0)       
    
    return d_today

def todays_time():
    '''
    get current tz adjusted time
    '''

    prm = main.models.Parameters.objects.first()
    tmz = pytz.timezone(prm.experiment_time_zone)

    d_today = datetime.now(tmz)

    return d_today.time()


