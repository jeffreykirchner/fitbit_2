'''
pull fitbit metrics
'''

import logging
import requests
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

def get_fitbit_metrics(fitbit_user, metrics_dict):
    '''
    metric_dict: {metric_label:fitbit_api_endpoint, ...}
    '''

    logger = logging.getLogger(__name__)
    
    logger.info(f"get_fitbit_metrics: user: {fitbit_user}, {metrics_dict}")

    data = {'fitbit_user' : fitbit_user, 'metrics_dict': metrics_dict}

    headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}

    request_result = requests.post(f'{settings.FITBIT_MS_URL}/get-metrics',
                                   json=data,
                                   auth=(str(settings.FITBIT_MS_USERNAME), str(settings.FITBIT_MS_PASS)),
                                   headers=headers)
    
    # if request_result.status_code == 500:        
    #     logger.warning(f'send_mass_email_service error: {request_result}')
    #     return {"mail_count":0, "error_message":"Mail service error"}
   
    logger.info(f"get_fitbit_metrics response: {request_result.json()}")

    return request_result.json()