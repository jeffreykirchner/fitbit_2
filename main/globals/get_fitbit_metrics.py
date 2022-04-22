'''
pull fitbit metrics
'''

import logging
from async_timeout import timeout
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

    try:
        request_result = requests.post(f'{settings.FITBIT_MS_URL}/get-metrics',
                                    json=data,
                                    auth=(str(settings.FITBIT_MS_USERNAME), str(settings.FITBIT_MS_PASS)),
                                    headers=headers,
                                    timeout=10)
    except requests.Timeout:
        logger.error(f"get_fitbit_metrics timeout: {data}")
        return {"status":"fail","message":"timeout", "result":{}}
    except requests.ConnectionError:
        logger.error(f"get_fitbit_metrics connection error: {data}")
        return {"status":"fail","message":"timeout", "result":{}} 
   
    logger.info(f"get_fitbit_metrics response: {request_result.json()}")

    return request_result.json()