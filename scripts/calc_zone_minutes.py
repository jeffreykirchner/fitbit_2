from main.models import SessionPlayerPeriod

#take session id from the command line
session_id = input("Enter session id: ")

for spp in SessionPlayerPeriod.objects.filter(fitbit_heart_time_series__isnull=False, session_player__session__id=session_id):
    spp.check_fitbit_age()
    spp.calc_zone_minutes_from_heart_rate_time_series()
