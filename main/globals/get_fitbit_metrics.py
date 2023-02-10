'''
pull fitbit metrics
'''

from datetime import datetime

import logging
from async_timeout import timeout
import requests
import json
import sys
import pytz

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

import main

def get_fitbit_metrics(fitbit_user, metrics_dict):
    '''
    metric_dict: {metric_label:fitbit_api_endpoint, ...}
    '''

    logger = logging.getLogger(__name__)
    
    logger.info(f"get_fitbit_metrics: user: {fitbit_user}, {metrics_dict}")

    #return test data during unit test
    if hasattr(sys, '_called_from_test'):        
        return get_fitbit_metrics_test()


    data = {'fitbit_user' : fitbit_user, 'metrics_dict': metrics_dict}

    headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}

    try:
        request_result = requests.post(f'{settings.FITBIT_MS_URL}/get-metrics',
                                    json=data,
                                    auth=(str(settings.FITBIT_MS_USERNAME), str(settings.FITBIT_MS_PASS)),
                                    headers=headers,
                                    timeout=30)
    except requests.Timeout:
        logger.error(f"get_fitbit_metrics timeout: {data}")
        return {"status":"fail","message":"timeout", "result":{}}
    except requests.ConnectionError:
        logger.error(f"get_fitbit_metrics connection error: {data}")
        return {"status":"fail","message":"timeout", "result":{}} 
   
    logger.info(f"get_fitbit_metrics response: {request_result.json()}")

    return request_result.json()

def get_fitbit_metrics_test():
    '''
    return simulated metric pull for unit tests
    '''
    logger = logging.getLogger(__name__)
    logger.info(f"Fitbit API unit test simulator")

    data = {'status': 'success', 'message': 'metrics pulled successfully',
            'result': {
            'devices': {'status': 'success', 'message': '', 'result': [{'battery': 'High', 'batteryLevel': 96, 'deviceVersion': 'Charge 4', 'features': [], 'id': '2006907148', 'lastSyncTime': '2022-05-06T09:00:17.000', 'mac': 'CE97B66838E7', 'type': 'TRACKER'}]},
            'fitbit_profile': {'status': 'success', 'message': '', 
                               'result': {'user': {'age': 91, 'ambassador': False, 'autoStrideEnabled': True, 'avatar': 'https://asset-service.fitbit.com/460ed99f-1e50-11b2-7f7f-7f7f7f7f7f7f_profile_100_square.jpg', 'avatar150': 'https://asset-service.fitbit.com/460ed99f-1e50-11b2-7f7f-7f7f7f7f7f7f_profile_150_square.jpg', 'avatar640': 'https://asset-service.fitbit.com/460ed99f-1e50-11b2-7f7f-7f7f7f7f7f7f_profile_640_square.jpg', 'averageDailySteps': 1972, 'challengesBeta': True, 'clockTimeDisplayFormat': '12hour', 'corporate': False, 'corporateAdmin': False, 'dateOfBirth': '1911-11-11', 'displayName': 'Adam Smith', 'displayNameSetting': 'name', 'distanceUnit': 'en_US', 'encodedId': 'abc123', 'features': {'exerciseGoal': True}, 'firstName': 'Adam', 'fullName': 'Adam Smaith', 'gender': 'MALE', 'glucoseUnit': 'en_US', 'height': 68.03149606299212, 'heightUnit': 'en_US', 'isBugReportEnabled': False, 'isChild': False, 'isCoach': False, 'languageLocale': 'en_US', 'lastName': 'Smith', 'legalTermsAcceptRequired': False, 'locale': 'en_US', 'memberSince': '2016-06-01', 'mfaEnabled': False, 'offsetFromUTCMillis': -25200000, 'sdkDeveloper': False, 'sleepTracking': 'Normal', 'startDayOfWeek': 'SUNDAY', 'strideLengthRunning': 44.960629921259844, 'strideLengthRunningType': 'auto', 'strideLengthWalking': 28.228346456692915, 'strideLengthWalkingType': 'auto', 'swimUnit': 'en_US', 'temperatureUnit': 'en_US', 'timezone': 'America/Los_Angeles',
                                                   'topBadges': [{'badgeGradientEndColor': 'B0DF2A', 'badgeGradientStartColor': '00A550', 'badgeType': 'DAILY_STEPS', 'category': 'Daily Steps', 'cheers': [], 'dateTime': '2022-04-25', 'description': '5,000 steps in a day', 'earnedMessage': 'Congrats on earning your first Boat Shoe badge!', 'encodedId': '228TQ4', 'image100px': 'https://badges.fitbit.com/images/badges_new/100px/badge_daily_steps5k.png', 'image125px': 'https://badges.fitbit.com/images/badges_new/125px/badge_daily_steps5k.png', 'image300px': 'https://badges.fitbit.com/images/badges_new/300px/badge_daily_steps5k.png', 'image50px': 'https://badges.fitbit.com/images/badges_new/badge_daily_steps5k.png', 'image75px': 'https://badges.fitbit.com/images/badges_new/75px/badge_daily_steps5k.png', 'marketingDescription': "You've walked 5,000 steps And earned the Boat Shoe badge!", 'mobileDescription': 'Congratulations on cruising your way to the first Fitbit daily step badge.', 'name': 'Boat Shoe (5,000 steps in a day)', 'shareImage640px': 'https://badges.fitbit.com/images/badges_new/386px/shareLocalized/en_US/badge_daily_steps5k.png', 'shareText': 'I took 5,000 steps and earned the Boat Shoe badge! #Fitbit', 'shortDescription': '5,000 steps', 'shortName': 'Boat Shoe', 'timesAchieved': 15, 'value': 5000}, 
                                                                 {'badgeGradientEndColor': '38D7FF', 'badgeGradientStartColor': '2DB4D7', 'badgeType': 'LIFETIME_DISTANCE', 'category': 'Lifetime Distance', 'cheers': [], 'dateTime': '2022-04-12', 'description': '70 lifetime miles', 'earnedMessage': "Whoa! You've earned the Penguin March badge!", 'encodedId': '22B8M7', 'image100px': 'https://badges.fitbit.com/images/badges_new/100px/badge_lifetime_miles70.png', 'image125px': 'https://badges.fitbit.com/images/badges_new/125px/badge_lifetime_miles70.png', 'image300px': 'https://badges.fitbit.com/images/badges_new/300px/badge_lifetime_miles70.png', 'image50px': 'https://badges.fitbit.com/images/badges_new/badge_lifetime_miles70.png', 'image75px': 'https://badges.fitbit.com/images/badges_new/75px/badge_lifetime_miles70.png', 'marketingDescription': "By reaching 70 lifetime miles, you've earned the Penguin March badge!", 'mobileDescription': 'You matched the distance of the March of the Penguins—the annual trip emperor penguins make to their breeding grounds.', 'name': 'Penguin March (70 lifetime miles)', 'shareImage640px': 'https://badges.fitbit.com/images/badges_new/386px/shareLocalized/en_US/badge_lifetime_miles70.png', 'shareText': 'I covered 70 miles with my #Fitbit and earned the Penguin March badge.', 'shortDescription': '70 miles', 'shortName': 'Penguin March', 'timesAchieved': 1, 'unit': 'MILES', 'value': 70}, 
                                                                 {'badgeGradientEndColor': '00D3D6', 'badgeGradientStartColor': '007273', 'badgeType': 'DAILY_FLOORS', 'category': 'Daily Climb', 'cheers': [], 'dateTime': '2022-04-23', 'description': '10 floors in a day', 'earnedMessage': 'Congrats on earning your first Happy Hill badge!', 'encodedId': '228TTM', 'image100px': 'https://badges.fitbit.com/images/badges_new/100px/badge_daily_floors10.png', 'image125px': 'https://badges.fitbit.com/images/badges_new/125px/badge_daily_floors10.png', 'image300px': 'https://badges.fitbit.com/images/badges_new/300px/badge_daily_floors10.png', 'image50px': 'https://badges.fitbit.com/images/badges_new/badge_daily_floors10.png', 'image75px': 'https://badges.fitbit.com/images/badges_new/75px/badge_daily_floors10.png', 'marketingDescription': "You've climbed 10 floors to earn the Happy Hill badge!", 'mobileDescription': "You're taking yourself to new heights and taking home the first badge!", 'name': 'Happy Hill (10 floors in a day)', 'shareImage640px': 'https://badges.fitbit.com/images/badges_new/386px/shareLocalized/en_US/badge_daily_floors10.png', 'shareText': 'I climbed 10 flights of stairs and earned the Happy Hill badge! #Fitbit', 'shortDescription': '10 floors', 'shortName': 'Happy Hill', 'timesAchieved': 8, 'value': 10}], 'weight': 137.0, 'weightUnit': 'en_US'}}}, 
            'fitbit_activities_td': {'status': 'success', 'message': '', 'result': {'activities': [{'activeDuration': 819000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 4, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 8, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 16}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 1, 'name': 'lightly'}, {'minutes': 2, 'name': 'fairly'}, {'minutes': 11, 'name': 'very'}], 'activityName': 'Outdoor Bike', 'activityTypeId': 1071, 'averageHeartRate': 122, 'calories': 96, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-04-27/2022-04-27/1min/time/17:19/17:33.json', 'duration': 819000, 'elevationGain': 10, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-04-27/2022-04-27/1sec/time/17:19:30/17:33:09.json', 'heartRateZones': [{'caloriesOut': 12.951799999999992, 'max': 110, 'min': 30, 'minutes': 1, 'name': 'Out of Range'}, {'caloriesOut': 51.8072, 'max': 133, 'min': 110, 'minutes': 8, 'name': 'Fat Burn'}, {'caloriesOut': 31.126099999999997, 'max': 161, 'min': 133, 'minutes': 4, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-04-28T00:37:23.000Z', 'logId': 47660651413, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 819000, 'originalStartTime': '2022-04-27T17:19:30.000-07:00', 'startTime': '2022-04-27T17:19:30.000-07:00', 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47660651413.tcx'}, 
                                                                                                {'activeDuration': 717000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 0, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 1, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 1}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 0, 'name': 'lightly'}, {'minutes': 5, 'name': 'fairly'}, {'minutes': 7, 'name': 'very'}], 'activityName': 'Walk', 'activityTypeId': 90013, 'averageHeartRate': 104, 'calories': 73, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-04-27/2022-04-27/1min/time/20:23/20:35.json', 'duration': 717000, 'elevationGain': 0, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-04-27/2022-04-27/1sec/time/20:23:49/20:35:46.json', 'heartRateZones': [{'caloriesOut': 67.0569, 'max': 110, 'min': 30, 'minutes': 10, 'name': 'Out of Range'}, {'caloriesOut': 6.0581, 'max': 133, 'min': 110, 'minutes': 1, 'name': 'Fat Burn'}, {'caloriesOut': 0, 'max': 161, 'min': 133, 'minutes': 0, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-04-28T03:38:10.000Z', 'logId': 47662906829, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 717000, 'originalStartTime': '2022-04-27T20:23:49.000-07:00', 'startTime': '2022-04-27T20:23:49.000-07:00', 'steps': 1099, 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47662906829.tcx'}, 
                                                                                                {'activeDuration': 820000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 1, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 8, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 10}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 1, 'name': 'lightly'}, {'minutes': 3, 'name': 'fairly'}, {'minutes': 10, 'name': 'very'}], 'activityName': 'Outdoor Bike', 'activityTypeId': 1071, 'averageHeartRate': 116, 'calories': 95, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-04-28/2022-04-28/1min/time/9:45/9:59.json', 'duration': 820000, 'elevationGain': 10, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-04-28/2022-04-28/1sec/time/09:45:57/09:59:37.json', 'heartRateZones': [{'caloriesOut': 35.51299999999999, 'max': 110, 'min': 30, 'minutes': 4, 'name': 'Out of Range'}, {'caloriesOut': 53.2695, 'max': 133, 'min': 110, 'minutes': 8, 'name': 'Fat Burn'}, {'caloriesOut': 6.4759, 'max': 161, 'min': 133, 'minutes': 1, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-04-28T17:11:41.000Z', 'logId': 47678853915, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 820000, 'originalStartTime': '2022-04-28T09:45:57.000-07:00', 'startTime': '2022-04-28T09:45:57.000-07:00', 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47678853915.tcx'}, 
                                                                                                {'activeDuration': 870000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 0, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 6, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 6}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 0, 'name': 'lightly'}, {'minutes': 4, 'name': 'fairly'}, {'minutes': 10, 'name': 'very'}], 'activityName': 'Outdoor Bike', 'activityTypeId': 1071, 'averageHeartRate': 115, 'calories': 91, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-05-02/2022-05-02/1min/time/17:02/17:16.json', 'duration': 870000, 'elevationGain': 50, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-05-02/2022-05-02/1sec/time/17:02:03/17:16:33.json', 'heartRateZones': [{'caloriesOut': 49.718199999999996, 'max': 110, 'min': 30, 'minutes': 8, 'name': 'Out of Range'}, {'caloriesOut': 41.5711, 'max': 133, 'min': 110, 'minutes': 6, 'name': 'Fat Burn'}, {'caloriesOut': 0, 'max': 161, 'min': 133, 'minutes': 0, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-05-03T00:32:13.000Z', 'logId': 47772153500, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 870000, 'originalStartTime': '2022-05-02T17:02:03.000-07:00', 'startTime': '2022-05-02T17:02:03.000-07:00', 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47772153500.tcx'}, 
                                                                                                {'activeDuration': 717000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 0, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 7, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 7}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 1, 'name': 'lightly'}, {'minutes': 4, 'name': 'fairly'}, {'minutes': 7, 'name': 'very'}], 'activityName': 'Walk', 'activityTypeId': 90013, 'averageHeartRate': 107, 'calories': 74, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-05-02/2022-05-02/1min/time/20:19/20:31.json', 'duration': 717000, 'elevationGain': 0, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-05-02/2022-05-02/1sec/time/20:19:11/20:31:08.json', 'heartRateZones': [{'caloriesOut': 30.081599999999995, 'max': 110, 'min': 30, 'minutes': 4, 'name': 'Out of Range'}, {'caloriesOut': 43.6601, 'max': 133, 'min': 110, 'minutes': 7, 'name': 'Fat Burn'}, {'caloriesOut': 0, 'max': 161, 'min': 133, 'minutes': 0, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-05-03T03:48:14.000Z', 'logId': 47773928075, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 717000, 'originalStartTime': '2022-05-02T20:19:11.000-07:00', 'startTime': '2022-05-02T20:19:11.000-07:00', 'steps': 1038, 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47773928075.tcx'}, 
                                                                                                {'activeDuration': 819000, 'activeZoneMinutes': {'minutesInHeartRateZones': [{'minuteMultiplier': 2, 'minutes': 0, 'order': 2, 'type': 'CARDIO', 'zoneName': 'Cardio'}, {'minuteMultiplier': 2, 'minutes': 0, 'order': 3, 'type': 'PEAK', 'zoneName': 'Peak'}, {'minuteMultiplier': 0, 'minutes': 0, 'order': 0, 'type': 'OUT_OF_ZONE', 'zoneName': 'Out of Range'}, {'minuteMultiplier': 1, 'minutes': 13, 'order': 1, 'type': 'FAT_BURN', 'zoneName': 'Fat Burn'}], 'totalMinutes': 13}, 'activityLevel': [{'minutes': 0, 'name': 'sedentary'}, {'minutes': 0, 'name': 'lightly'}, {'minutes': 2, 'name': 'fairly'}, {'minutes': 12, 'name': 'very'}], 'activityName': 'Outdoor Bike', 'activityTypeId': 1071, 'averageHeartRate': 121, 'calories': 99, 'caloriesLink': 'https://api.fitbit.com/1/user/-/activities/calories/date/2022-05-03/2022-05-03/1min/time/10:28/10:42.json', 'duration': 819000, 'elevationGain': 40, 'hasActiveZoneMinutes': True, 'heartRateLink': 'https://api.fitbit.com/1/user/-/activities/heart/date/2022-05-03/2022-05-03/1sec/time/10:28:59/10:42:38.json', 'heartRateZones': [{'caloriesOut': 7.938200000000009, 'max': 110, 'min': 30, 'minutes': 0, 'name': 'Out of Range'}, {'caloriesOut': 91.2893, 'max': 133, 'min': 110, 'minutes': 13, 'name': 'Fat Burn'}, {'caloriesOut': 0, 'max': 161, 'min': 133, 'minutes': 0, 'name': 'Cardio'}, {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}], 'lastModified': '2022-05-03T17:50:22.000Z', 'logId': 47790490503, 'logType': 'auto_detected', 'manualValuesSpecified': {'calories': False, 'distance': False, 'steps': False}, 'originalDuration': 819000, 'originalStartTime': '2022-05-03T10:28:59.000-07:00', 'startTime': '2022-05-03T10:28:59.000-07:00', 'tcxLink': 'https://api.fitbit.com/1/user/-/activities/47790490503.tcx'}], 'pagination': {'afterDate': '2022-04-27', 'limit': 100, 'next': '', 'offset': 0, 'previous': '', 'sort': 'asc'}}}, 
            'fitbit_heart_time_series_td': {'status': 'success', 'message': '', 
                                         'result': {'activities-heart': [{'dateTime': '2022-04-27', 'value': {'customHeartRateZones': [], 'heartRateZones': [{'caloriesOut': 1663.36625, 'max': 110, 'min': 30, 'minutes': 1424, 'name': 'Out of Range'}, 
                                                                                                                                                             {'caloriesOut': 69.3548, 'max': 133, 'min': 110, 'minutes': 12, 'name': 'Fat Burn'}, 
                                                                                                                                                             {'caloriesOut': 31.126099999999997, 'max': 161, 'min': 133, 'minutes': 4, 'name': 'Cardio'}, 
                                                                                                                                                             {'caloriesOut': 0, 'max': 220, 'min': 161, 'minutes': 0, 'name': 'Peak'}]}}], 
                                                                                                                                          'activities-heart-intraday': {'dataset': [{'time': '10:36:00', 'value': 73}, {'time': '10:37:00', 'value': 75}, {'time': '16:36:00', 'value': 80}, {'time': '16:37:00', 'value': 76}, {'time': '16:38:00', 'value': 75}, {'time': '16:39:00', 'value': 76}, {'time': '16:40:00', 'value': 71}, {'time': '16:41:00', 'value': 76}, {'time': '16:42:00', 'value': 72}, {'time': '16:43:00', 'value': 75}, {'time': '16:44:00', 'value': 68}, {'time': '16:45:00', 'value': 73}, {'time': '16:46:00', 'value': 75}, {'time': '16:47:00', 'value': 74}, {'time': '16:48:00', 'value': 75}, {'time': '16:49:00', 'value': 76}, {'time': '16:50:00', 'value': 78}, {'time': '16:51:00', 'value': 75}, {'time': '16:52:00', 'value': 76}, {'time': '16:53:00', 'value': 80}, {'time': '16:54:00', 'value': 78}, {'time': '16:55:00', 'value': 80}, {'time': '16:56:00', 'value': 69}, {'time': '16:57:00', 'value': 71}, {'time': '16:58:00', 'value': 70}, {'time': '16:59:00', 'value': 73}, {'time': '17:00:00', 'value': 76}, {'time': '17:01:00', 'value': 75}, {'time': '17:02:00', 'value': 77}, {'time': '17:03:00', 'value': 75}, {'time': '17:04:00', 'value': 73}, {'time': '17:05:00', 'value': 76}, {'time': '17:06:00', 'value': 79}, {'time': '17:07:00', 'value': 75}, {'time': '17:08:00', 'value': 76}, {'time': '17:09:00', 'value': 75}, {'time': '17:10:00', 'value': 75}, {'time': '17:11:00', 'value': 76}, {'time': '17:12:00', 'value': 77}, {'time': '17:13:00', 'value': 83}, {'time': '17:14:00', 'value': 99}, {'time': '17:15:00', 'value': 104}, {'time': '17:16:00', 'value': 111}, {'time': '17:17:00', 'value': 117}, {'time': '17:18:00', 'value': 100}, {'time': '17:19:00', 'value': 93}, {'time': '17:20:00', 'value': 118}, {'time': '17:21:00', 'value': 105}, {'time': '17:22:00', 'value': 115}, {'time': '17:23:00', 'value': 113}, {'time': '17:24:00', 'value': 118}, {'time': '17:25:00', 'value': 118}, {'time': '17:26:00', 'value': 129}, {'time': '17:27:00', 'value': 129}, {'time': '17:28:00', 'value': 134}, {'time': '17:29:00', 'value': 134}, {'time': '17:30:00', 'value': 135}, {'time': '17:31:00', 'value': 134}, {'time': '17:32:00', 'value': 122}, {'time': '17:33:00', 'value': 116}, {'time': '19:04:00', 'value': 69}, {'time': '19:05:00', 'value': 71}, {'time': '19:16:00', 'value': 64}, {'time': '19:17:00', 'value': 71}, {'time': '19:19:00', 'value': 63}, {'time': '19:20:00', 'value': 71}, {'time': '19:21:00', 'value': 64}, {'time': '19:22:00', 'value': 67}, {'time': '19:23:00', 'value': 73}, {'time': '20:17:00', 'value': 76}, {'time': '20:18:00', 'value': 81}, {'time': '20:19:00', 'value': 85}, {'time': '20:20:00', 'value': 83}, {'time': '20:21:00', 'value': 84}, {'time': '20:22:00', 'value': 84}, {'time': '20:23:00', 'value': 85}, {'time': '20:24:00', 'value': 86}, {'time': '20:25:00', 'value': 105}, {'time': '20:26:00', 'value': 107}, {'time': '20:27:00', 'value': 105}, {'time': '20:28:00', 'value': 109}, {'time': '20:29:00', 'value': 102}, {'time': '20:30:00', 'value': 101}, {'time': '20:31:00', 'value': 106}, {'time': '20:32:00', 'value': 113}, {'time': '20:33:00', 'value': 106}, {'time': '20:34:00', 'value': 107}, {'time': '20:35:00', 'value': 99}, {'time': '20:36:00', 'value': 84}, {'time': '20:37:00', 'value': 84}, {'time': '20:38:00', 'value': 81}, {'time': '20:39:00', 'value': 82}, {'time': '20:40:00', 'value': 86}, {'time': '20:41:00', 'value': 85}, {'time': '20:42:00', 'value': 84}, {'time': '20:43:00', 'value': 81}, {'time': '20:44:00', 'value': 82}, {'time': '20:45:00', 'value': 96}, {'time': '20:46:00', 'value': 95}, {'time': '20:47:00', 'value': 90}, {'time': '20:48:00', 'value': 89}, {'time': '20:49:00', 'value': 88}, {'time': '20:50:00', 'value': 84}], 'datasetInterval': 1, 'datasetType': 'minute'}}}
            }
    }

    prm = main.models.Parameters.objects.first()
    tmz = pytz.timezone(prm.experiment_time_zone)

    data["result"]["devices"]["result"][0]["lastSyncTime"] =  datetime.now(tmz).strftime("%Y-%m-%dT%H:%M:%S.%f")

    return data

