'''
websocket session list
'''
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync

import json
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.urls import reverse
from django.db.utils import IntegrityError
from channels.layers import get_channel_layer

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm
from main.forms import StaffEditNameEtcForm

from main.models import Session
from main.models import Parameters

from main.globals import send_mass_email_service
from main.globals import ExperimentPhase
from main.models.session_player_period import SessionPlayerPeriod

class StaffSessionConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    
        
    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["sessionKey"]
        self.connection_type = "staff"

        #build response
        message_data = {}
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)       

        self.session_id = message_data["session"]["id"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
    
    async def update_session(self, event):
        '''
        return a list of sessions
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f"Update Session: {event}")

        #build response
        message_data = {}
        message_data["status"] =  await sync_to_async(take_update_session_form)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def start_experiment(self, event):
        '''
        start experiment
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_start_experiment)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #Send message to staff page
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_start_experiment",
                     "message_text" : {"first_load_done" : "True"},
                     "sender_channel_name": self.channel_name},
                )
    
    async def reset_experiment(self, event):
        '''
        reset experiment, removes all trades, bids and asks
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_reset_experiment)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_reset_experiment",
                     "message_text" : {"first_load_done" : "True"},
                     "sender_channel_name": self.channel_name},
                )
    
    async def reset_connections(self, event):
        '''
        reset connection counts for experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_reset_connections)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_reset_connections",
                     "sender_channel_name": self.channel_name},
                )

    async def next_phase(self, event):
        '''
        advance to next phase in experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_next_phase)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_next_phase",
                     "data": message_data["status"],
                     "sender_channel_name": self.channel_name},
                )

    async def download_summary_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_summary_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_heart_rate_data(self, event):
        '''
        download heart rate data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_heart_rate_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_activities_data(self, event):
        '''
        download activties data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_activities_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_chat_data(self, event):
        '''
        download chat data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_chat_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def end_early(self, event):
        '''
        set the current period as the last period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_end_early)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_subject(self, event):
        '''
        set the name etc info of a subjec from staff screen
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_subject)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def email_list(self, event):
        '''
        take csv email list and load in to session players
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_email_list)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def send_invitations(self, event):
        '''
        send invitations to subjects
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_send_invitations)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def fill_with_test_data(self, event):
        '''
        send invitations to subjects
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_fill_with_test_data)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def get_pay_block(self, event):
        '''
        return the specified pay block
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_get_pay_block)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def force_check_in(self, event):
        '''
        force a subject to check in a given day
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_force_check_in)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def load_full_subject(self, event):
        '''
        return full subject object
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_load_full_subject)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def pull_time_series_data(self, event):
        '''
        pull timeseries data for session
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_pull_time_series_data)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        #get session json object
        result = await sync_to_async(take_get_session)(self.connection_uuid)

        message_data = {}
        message_data["session"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_experiment(self, event):
        '''
        update reset experiment
        '''
        #update subject count
        message_data = {}
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_connections(self, event):
        '''
        update reset experiment
        '''
        #update subject count
        message_data = {}
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        result = event["staff_result"]

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info("Connection update")

        #update not from a client
        if event["data"]["value"] == "fail":
            return

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_consent_form(self, event):
        '''
        send update of consent form status
        '''

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
#local async function

#local sync functions    
def take_get_session(session_key):
    '''
    return session with specified id
    param: session_key {uuid} session uuid
    '''
    session = None
    logger = logging.getLogger(__name__)

    try:        
        session = Session.objects.get(session_key=session_key)
        return session.json()
    except ObjectDoesNotExist:
        logger.warning(f"staff get_session session, not found: {session_key}")
        return {}

def take_update_session_form(session_id, data):
    '''
    take session form data and update session or return errors
    param: data {json} incoming form and session data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_update_session_form: {data}')

    #session_id = data["sessionID"]
    form_data = data["formData"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_session_form session, not found: {session_id}")
    
    form_data_dict = form_data

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]
    
    if session.started:
        form_data_dict["start_date"] = session.get_start_date_string_widget()

    form = SessionForm(form_data_dict, instance=session)

    if form.is_valid():
        #print("valid form")                
        form.save()          

        if not session.started:    
            session.update_end_date()

        return {"value" : "success", "session" : session.json()}                      
                                
    logger.info("Invalid session form")
    return {"status":"fail", "errors":dict(form.errors.items())}

def take_start_experiment(session_id, data):
    '''
    start experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Start Experiment: {data}")

    #session_id = data["sessionID"]
    with transaction.atomic():
        session = Session.objects.get(id=session_id)

        if not session.started:
            session.start_experiment()

        value = "success"
    
    return {"value" : value, "started" : session.started}

def take_reset_experiment(session_id, data):
    '''
    reset experiment remove bids and asks
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Reset Experiment: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if session.started:
        session.reset_experiment()  

    value = "success"
    
    return {"value" : value, "started" : session.started}

def take_reset_connections(session_id, data):
    '''
    reset connection counts for experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Reset connection counts: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if not session.started:
        session.reset_connection_counts()  

    value = "success"
    
    return {"value" : value, "started" : session.started}

def take_download_summary_data(session_id):
    '''
    download summary data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_summary_csv()}

def take_download_heart_rate_data(session_id):
    '''
    download heart rate data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_heart_rate_csv()}

def take_download_activities_data(session_id):
    '''
    download activities data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_activities_csv()}

def take_download_chat_data(session_id):
    '''
    download chat data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_chat_csv()}

def take_end_early(session_id):
    '''
    make the current period the last period
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f'take_end_early: Session {session_id}')

    session = Session.objects.get(id=session_id)

    session_period = session.get_current_session_period()

    if session_period:
        session.session_periods.filter(period_number__gt = session_period.period_number).delete()
        session.parameter_set.parameter_set_periods.filter(period_number__gt = session_period.period_number).delete()

        for p in session.parameter_set.parameter_set_periods.all():
            if p.graph_1_start_period_number > session_period.period_number:
                p.graph_1_start_period_number = session_period.period_number
                p.save()
            
            if p.graph_1_end_period_number > session_period.period_number:
                p.graph_1_end_period_number = session_period.period_number
                p.save()
            
            if p.graph_2_start_period_number > session_period.period_number:
                p.graph_2_start_period_number = session_period.period_number
                p.save()
            
            if p.graph_2_end_period_number > session_period.period_number:
                p.graph_2_end_period_number = session_period.period_number
                p.save()
        
        session.update_end_date()


    return {"value" : "success", "session" : session.json()}

def take_update_subject(session_id, data):
    '''
    take update subject info from staff screen
    param: data {json} incoming form and session data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_update_subject: {data}')

    #session_id = data["sessionID"]
    form_data = dict(data["formData"])

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_session_form session, not found: {session_id}")
        return {"status":"fail", "message":"session not found"}

    form = StaffEditNameEtcForm(form_data)

    if form.is_valid():

        session_player = session.session_players.get(id=form_data["id"])
        session_player.name = form.cleaned_data["name"]
        session_player.student_id = form.cleaned_data["student_id"]
        session_player.email = form.cleaned_data["email"]
        session_player.group_number = form.cleaned_data["group_number"]
        session_player.disabled = True if form.cleaned_data["disabled"] == "1" else False
        session_player.fitbit_user_id =  form.cleaned_data["fitbit_user_id"]
        
        try:
            session_player.save()              
        except IntegrityError as e:
            return {"value":"fail", "errors" : {f"email":["Email must be unique within session."]}}  

        return {"value":"success", "session_player" : session_player.json()}                      
                                
    logger.info("Invalid session form")
    return {"status":"fail", "errors":dict(form.errors.items())}

def take_send_invitations(session_id, data):
    '''
    send login link to subjects in session
    '''
    logger = logging.getLogger(__name__)
    logger.info(f'take_send_invitations: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_send_invitations session, not found: {session_id}")
        return {"status":"fail", "result":"session not found"}

    p = Parameters.objects.first()
    message = data["formData"]

    session.invitation_text =  message["text"]
    session.invitation_subject =  message["subject"]
    
    session.invitation_text  =  session.invitation_text .replace("[contact email]", p.contact_email)

    session.save()

    user_list = []
    for session_subject in session.session_players.exclude(email=None).exclude(email="").exclude(disabled=True):
        user_list.append({"email" : session_subject.email,
                          "variables": [{"name" : "log in link",
                                         "text" : p.site_url + reverse('subject_home', kwargs={'player_key': session_subject.player_key})
                                        }] 
                         })

    memo = f'Trade Steal: Session {session_id}, send invitations'

    result = send_mass_email_service(user_list, session.invitation_subject, session.invitation_text , session.invitation_text, memo)

    return {"value" : "success",
            "result" : {"email_result" : result,
                        "invitation_subject" : session.invitation_subject,
                        "invitation_text" : session.invitation_text }}

def take_email_list(session_id, data):
    '''
    take recruiter formated user list
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_email_list: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_send_invitations session, not found: {session_id}")
        return {"status":"fail", "result":"session not found"}
    
    raw_list = data["csv_data"]

    raw_list = raw_list.splitlines()

    counter = 1
    for i in range(len(raw_list)):
        raw_list[i] = re.split(r',|\t', raw_list[i])

        if raw_list[i][0] != "Last Name":
            p = session.session_players.filter(player_number=counter).first()

            if p:
                p.name = raw_list[i][0] + " " + raw_list[i][1]
                p.email = raw_list[i][2]
                p.student_id = raw_list[i][3]

                p.save()
            
            counter+=1
    
    return {"value" : "success", "result" : {"session":session.json()}}
            
def take_fill_with_test_data(session_id, data):
    '''
    fill subjects with test data up to this point in the experiment
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_take_fill_with_test_data: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_take_fill_with_test_data session, not found: {session_id}")
        return {"status":"fail", "result":"session not found"}
    
    session.fill_with_test_data()

    logger.info(f'take_take_fill_with_test_data: data filled')

    for player in session.session_players.all().prefetch_related("session_player_periods_b"):
        for session_period_player in player.session_player_periods_b.all():
            session_period_player.calc_and_store_payment()
    
    logger.info(f'take_take_fill_with_test_data: calc payments')
    
    return {"value" : "success",
            "session_players" : [p.json() for p in session.session_players.all()]}
    
def take_next_phase(session_id, data):
    '''
    move to next phase of the experiment
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_next_phase: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
        logger.info(f'take_next_phase phase: {session.current_experiment_phase}')
    except ObjectDoesNotExist:
        logger.warning(f"take_next_phase session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}
    
    if session.current_experiment_phase == ExperimentPhase.INSTRUCTIONS:
       session.current_experiment_phase = ExperimentPhase.RUN
    elif session.current_experiment_phase == ExperimentPhase.RUN:
         session.current_experiment_phase = ExperimentPhase.DONE
         session.finished = True
    
    session.save()

    return {"value" : "success",
            "current_experiment_phase" : session.current_experiment_phase,
            "finished" : session.finished}

def take_get_pay_block(session_id, data):
    '''
    return the the specifed pay block
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_get_pay_block: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
        pay_block_number = data["pay_block"]
    except ObjectDoesNotExist:
        logger.warning(f"take_get_pay_block session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}
    
    session.back_fill_for_pay_block(pay_block_number)

    return {"value" : "success",
            "pay_block_csv" : session.get_pay_block_csv(pay_block_number),}

def take_force_check_in(session_id, data):
    '''
    force a check in for a subject on a given day
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_force_check_in: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
        session_player_period = SessionPlayerPeriod.objects.get(id=data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_force_check_in session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}

    r = session_player_period.take_check_in(False)

    if r["status"] == "success":        
        session_player_period.check_in_forced = True
        session_player_period.save()

        pay_block = session_player_period.get_pay_block()

        session_player_period.session_player.calc_averages_for_block(pay_block)

        for i in session_player_period.session_player.get_group_members():
            i.calc_payments_for_block(pay_block)

    return {"value" : "success",
            "session_player_period" : session_player_period.json_for_staff(),}

def take_load_full_subject(session_id, data):
    '''
    force a check in for a subject on a given day
    '''
    logger = logging.getLogger(__name__)
    logger.info(f'take_load_full_subject: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=data["subject_id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_load_full_subject session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}

    
    return {"value" : "success",
            "session_player" : session_player.json_for_staff(),}

def take_pull_time_series_data(session_id, data):
    '''
    force a check in for a subject on a given day
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_pull_time_series_data: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_pull_time_series_data session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}

    for i in session.session_players.all():
        i.pull_secondary_time_series()

    return {"value" : "success",}


