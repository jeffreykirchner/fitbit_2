'''
staff view
'''
import logging
import json

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.shortcuts import redirect


from main.models import SessionPlayer

class SubjectFitbitRegistration(View):
    '''
    class based staff view
    '''
    template_name = "subject/subject_home.html"
    websocket_path = "subject-home"
    
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''
        try:
            
            session_player = SessionPlayer.objects.get(player_key=kwargs['player_key'])
            session_player.fitbit_user_id = kwargs['user_id']
            session_player.save()

        except ObjectDoesNotExist:
            raise Http404("Fitbit Registration Error.")
        
        return redirect('subject_home', player_key=session_player.player_key)
    