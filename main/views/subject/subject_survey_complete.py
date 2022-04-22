'''
subject survey complete view
'''
import logging
import json

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.shortcuts import render
from django.urls import reverse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from main.models import Parameters
from main.models import SessionPlayerPeriod

class SubjectSurveyCompleteView(View):
    '''
    class based staff view
    '''
    template_name = "subject/survey_complete.html"
    websocket_path = "subject-home"
    
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''

        try:
            session_player_period = SessionPlayerPeriod.objects.get(activity_key=kwargs['activity_key'])
            session_player_period.survey_complete = True    
            session_player_period.save()           

        except ObjectDoesNotExist:
            raise Http404("Subject not found.")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send) \
                     (str(session_player_period.session_player.channel_name), {
                        'type': 'survey_complete',
                        'message_text': {}
                      })

        parameters = Parameters.objects.first()

        return_link = reverse('subject_home', kwargs={'player_key': session_player_period.session_player.player_key})

        return render(request=request,
                      template_name=self.template_name,
                      context={"return_link" : return_link})
    