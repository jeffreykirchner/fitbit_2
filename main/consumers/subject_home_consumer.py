'''
websocket session list
'''
from datetime import datetime
from datetime import timedelta
from wsgiref.simple_server import software_version
from asgiref.sync import sync_to_async

import logging
import copy
import json
import string
import pytz
from copy import copy

from django.core.exceptions import  ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import EndGameForm

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat

from main.globals import round_half_away_from_zero

from main.decorators import check_sesison_started_ws

import main
from main.models.parameters import Parameters

class SubjectHomeConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    session_player_id = 0   #session player id number
    
    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["playerKey"]
        self.connection_type = "subject"

        self.session_id = await sync_to_async(take_get_session_id)(self.connection_uuid)

        await self.update_local_info(event)

        result = await sync_to_async(take_get_session_subject)(self.session_player_id, event["message_text"])

        #build response
        message_data = {"status":{}}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
   
    async def chat(self, event):
        '''
        take chat from client
        '''        
        r = await sync_to_async(take_chat)(self.session_id, self.session_player_id, event["message_text"])

        if r["value"] == "fail":
            await self.send(text_data=json.dumps({'message': r}, cls=DjangoJSONEncoder))
            return

        event_result = r["result"]

        subject_result = {}
        subject_result["sesson_player_target"] = event_result.get("sesson_player_target", -1)
        subject_result["chat"] = event_result["chat_for_subject"]
        subject_result["value"] = r["value"]

        staff_result = {}
        staff_result["chat"] = event_result["chat_for_staff"]

        message_data = {}
        message_data["status"] = subject_result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        #if success send to all connected clients
        if r["value"] == "success":

            for p in event_result["recipients"]:
                if p != "":
                    await self.channel_layer.send(
                        p,
                        {"type": "update_chat",
                        "subject_result": subject_result,
                        "staff_result": staff_result,
                        "sender_channel_name": self.channel_name}
                    )

    async def next_instruction(self, event):
        '''
        advance instruction page
        '''
        result = await sync_to_async(take_next_instruction)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_next_instruction",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )
    
    async def finish_instructions(self, event):
        '''
        fisish instructions
        '''
        result = await sync_to_async(take_finish_instructions)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_finish_instructions",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    async def check_in(self, event):
        '''
        fisish instructions
        '''
        r = await sync_to_async(take_check_in)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = r

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        event_result = r["result"]

        if r["value"] == "success":

            subject_result = {"status" : "success",
                              "result" :  {"session": event_result["session"]}}

            for p in event_result["recipients"]:

                await self.channel_layer.send(
                    p,
                    {"type": "update_check_in",
                     "result" : json.dumps(subject_result, cls=DjangoJSONEncoder),
                     "sender_channel_name": self.channel_name}
                )
    
    async def survey_complete(self, event):
        '''
        survey complete
        '''
        result = await sync_to_async(take_survey_complete)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def help_doc_subject(self, event):
        '''
        help doc request
        '''
        result = await sync_to_async(take_help_doc_subject)(self.session_id, self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def consent_form(self, event):
        '''
        agree to consent form
        '''
        r = await sync_to_async(take_consent_form)(self.session_id, self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = r

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if r["value"] == "success":
            update_result = {"value" : "success",
                             "result" : {"player_id" : self.session_player_id, "consent_form_required":r["result"]["consent_form_required"]}}

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_consent_form",
                 "data": update_result,
                 "sender_channel_name": self.channel_name},
            )

    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        await self.update_local_info(event)

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_experiment(self, event):
        '''
        reset experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''

        message_data = {}
        message_data["status"] =  event["subject_result"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.channel_name == event['sender_channel_name']:
            return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_check_in(self, event):
        '''
        send chat to clients, if clients can view it
        '''

        message_data = {}
        message_data["status"] =  json.loads(event["result"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.channel_name == event['sender_channel_name']:
            return

        session_player_json = result = await sync_to_async(take_get_session_player_json)(self.session_player_id)

        if not session_player_json:
            return

        message_data["status"]["result"]["session_player"] = session_player_json

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_local_info(self, event):
        '''
        update connection's information
        '''
        result = await sync_to_async(take_update_local_info)(self.session_id, self.connection_uuid, self.channel_name, event)

        logger = logging.getLogger(__name__) 
        logger.info(f"update_local_info {result}")

        self.session_player_id = result["session_player_id"]

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
    
    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        result = await sync_to_async(take_update_next_phase)(self.session_id, self.session_player_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
    
    async def update_finish_instructions(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
    
    async def update_consent_form(self, event):
        '''
        no group broadcast consent form status
        '''

#local sync functions  
def take_get_session_subject(session_player_id, data):
    '''
    get session info for subject
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take_get_session_subject: {session_player_id} {data}")

    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    #session = Session.objects.get(id=session_id)
    fitbit_error_message = ""
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)
        first_load_done = data["first_load_done"]

        show_fitbit_connect = False

        if session_player.fitbit_user_id == "":
            show_fitbit_connect = True
            fitbit_error_message = "Connect your fitbit the app."

        if not first_load_done and not show_fitbit_connect:        
            value = session_player.pull_todays_metrics()
    
            if value["status"] == "fail":
                if value["message"] == "re-connect required" or \
                   value["message"] == "user not found" or \
                   value["message"] == "no fitbit user id":

                    show_fitbit_connect = True
                    fitbit_error_message = "Connect your fitbit the app."
                elif value["message"] == "Not synced today":
                    fitbit_error_message = "Sync your fitbit to your phone."
                else:
                    fitbit_error_message = "Fitbit is not available, try again later."
            else:
                session_player.pull_missing_metrics()
                pass                

        return {"session" : session_player.session.json_for_subject(session_player), 
                "show_fitbit_connect" : show_fitbit_connect,
                "fitbit_error_message" : fitbit_error_message,
                "session_player" : session_player.json() }

    except ObjectDoesNotExist:
        return {"session" : None, 
                "session_player" : None}

def take_get_session_player_json(session_player_id):
    '''
    return session player with specified id
    '''
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)
    except ObjectDoesNotExist:
        return None

    return session_player.json()

def take_get_session_id(player_key):
    '''
    get the session id for the player_key
    '''
    try:
        session_player = SessionPlayer.objects.get(player_key=player_key)
    except ObjectDoesNotExist:
        return None
        
    return session_player.session.id
  
def take_chat(session_id, session_player_id, data):
    '''
    take chat from client
    sesson_id : int : id of session
    session_player_id : int : id of session player
    data : json : incoming json data
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take chat: {session_id} {session_player_id} {data}")

    try:
        chat_text = data["text"]
    except KeyError:
         return {"value" : "fail", "result" : {"message" : "Invalid chat."}}

    result = {}
    #result["recipients"] = []

    session = Session.objects.get(id=session_id)
    session_player = session.session_players.get(id=session_player_id)
    
    session_player_chat = SessionPlayerChat()

    session_player_chat.session_player = session_player
    session_player_chat.session_period = session.get_current_session_period()

    if not session.started:
        return  {"value" : "fail", "result" : {"message" : "Session not started."}, }
        
    if session.finished:
        return {"value" : "fail", "result" : {"message" : "Session finished."}}

    if session.current_experiment_phase != main.globals.ExperimentPhase.RUN:
            return {"value" : "fail", "result" : {"message" : "Session not running."}}

    #return group channel ids
    result["recipients"] = session.get_group_channel_list(session_player.group_number)

    #if more than one hour since last chat message then show date

    c = main.models.SessionPlayerChat.objects.filter(session_player__in=session.session_players.all()) \
                                             .filter(session_player__group_number=session_player.group_number) \
                                             .order_by('timestamp').last()

    if not c:
        session_player_chat.show_time_stamp = True
    elif datetime.now(pytz.UTC) - c.timestamp>timedelta(minutes=60):
        session_player_chat.show_time_stamp = True
        
    session_player_chat.text = chat_text
    session_player_chat.save()
    
    result["chat_for_subject"] = session_player_chat.json_for_subject()
    result["chat_for_staff"] = session_player_chat.json_for_staff()

    session_player_chat.save()

    return {"value" : "success", "result" : result}

def take_update_local_info(session_id, player_key, channel_name, data):
    '''
    update connection's information
    '''

    try:
        session_player = SessionPlayer.objects.get(player_key=player_key)
        session_player.channel_name = channel_name
        session_player.save()

        return {"session_player_id" : session_player.id}
    except ObjectDoesNotExist:      
        return {"session_player_id" : None}

def take_update_next_phase(session_id, session_player_id):
    '''
    return information about next phase of experiment
    '''

    logger = logging.getLogger(__name__) 

    try:
        session = Session.objects.get(id=session_id)
        session_player = SessionPlayer.objects.get(id=session_player_id)


        return {"value" : "success",
                "session" : session_player.session.json_for_subject(session_player),
                "session_player" : session_player.json(),
                "session_players" : [p.json_for_subject(session_player) for p in session.session_players.all()]}

    except ObjectDoesNotExist:
        logger.warning(f"take_update_next_phase: session not found, session {session_id}, session_player_id {session_player_id}")
        return {"value" : "fail", "result" : {}, "message" : "Update next phase error"}

def take_next_instruction(session_id, session_player_id, data):
    '''
    take show next instruction page
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take next instruction: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        direction = data["direction"]

        #move to next instruction
        if direction == 1:
            #advance furthest instruction complete
            if session_player.current_instruction_complete < session_player.current_instruction:
                session_player.current_instruction_complete = copy(session_player.current_instruction)

            if session_player.current_instruction < session.parameter_set.instruction_set.instructions.count():
                session_player.current_instruction += 1
        elif session_player.current_instruction > 1:
             session_player.current_instruction -= 1

        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction not found: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."} 
    except KeyError:
        logger.warning(f"take_next_instruction key error: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."}       
    
    return {"value" : "success",
            "result" : {"current_instruction" : session_player.current_instruction,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player.current_instruction_complete, 
                        }}

def take_finish_instructions(session_id, session_player_id, data):
    '''
    take finish instructions
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take finish instructions: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        session_player.current_instruction_complete = session.parameter_set.instruction_set.instructions.count()
        session_player.instructions_finished = True
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : ""}       
    
    return {"value" : "success",
            "result" : {"instructions_finished" : session_player.instructions_finished,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player.current_instruction_complete, 
                        }}

def take_check_in(session_id, session_player_id, data):
    '''
    take check in
    '''    
    status = "success"
    error_message = ""
    result = {}

    logger = logging.getLogger(__name__) 
    logger.info(f"Take check in: session {session_id}, player {session_player_id}, {data}")

    try:       
        p = Parameters.objects.first()

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)
        session_player_period = session_player.get_todays_session_player_period()

        software_version = data["software_version"]
        client_current_period = data["current_period"]

        # value = session_player.pull_todays_metrics()

    except ObjectDoesNotExist:
        status = "fail"
        error_message = "Session not available."
        logger.warning(f"take_check_in : {session_player_id}") 
    
    #software version
    if status == "success":
        if p.software_version != software_version:
            status = "fail"
            error_message = "Refresh your browser."
    
    #period number
    if status == "success":
        if session_player_period.session_period.period_number != client_current_period:
            status = "fail"
            error_message = "Refresh your browser."
    
    #check for survey
    if status == "success":
        if session_player.get_current_survey_link() != "":
            status = "fail"
            error_message = "Refresh your browser."

    #session started
    if status == "success":
        if not session.started:
            status = "fail"
            error_message = "Session not started."
    
    #session not finsihed
    if status == "success":
        if session.finished:
            status = "fail"
            error_message = "Session complete."
    
    #player disabled
    if status == "success":
        if session_player.disabled:
            status = "fail"
            error_message = "Session complete."

    #wrist time
    if status == "success":
        if not session_player_period.wrist_time_met():
            status = "fail"
            error_message = "You have not worn your Fitbit long enough today."
    
    #fitbit sync
    if status == "success":
        if not session_player.fitbit_synced_last_30_min():
            status = "fail"
            error_message = "Sync your Fitbit to your phone."

    if status == "success":
        r = session_player_period.take_check_in(True)

        if r["status"] == "fail":
            status = "fail"
            error_message = "Fitbit is not available, try again later."
       
    if status == "success":
        result = {"session_player" : session_player.json(),
                  "session" : session.json_for_subject(session_player),
                  "recipients" :  session.get_group_channel_list(session_player.group_number)}
    else:
        result = { "error_message" : error_message,
                 }

    return {"value" : status,
            "result" : result}

def take_survey_complete(session_id, session_player_id, data):
    '''
    take survey complete
    '''    
    status = "success"
    error_message = ""
    result = {}

    logger = logging.getLogger(__name__) 
    logger.info(f"Take survey complete: session {session_id}, player {session_player_id}, {data}")

    try:       
        p = Parameters.objects.first()

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)
        session_player_period = session_player.get_todays_session_player_period()

    except ObjectDoesNotExist:
        status = "fail"
        error_message = "Session not available."
        logger.warning(f"take_survey_complete : {session_player_id}") 
    
    
    return {"value" : status,
            "result" : {"session_player" : session_player.json()}}

def take_help_doc_subject(session_id, session_player_id, data):
    '''
    help doc text request
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take help doc subject: {data}")

    try:
        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)
        help_doc = session_player.get_help_doc(data["title"])
    except ObjectDoesNotExist:
        logger.warning(f"take_help_doc not found : {data}")
        return {"value" : "fail", "message" : "Document Not Found."}

    return {"value" : "success",
            "result" : {"help_doc" : help_doc}}

def take_consent_form(session_id, session_player_id, data):
    '''
    agree to consent form
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take agree to consent form: {data}")

    try:
        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)
        
        session_player.consent_form_required = False
        session_player.save()
    except ObjectDoesNotExist:
        logger.warning(f"take_help_doc not found : {data}")
        return {"value" : "fail", "reslut" : {}}

    return {"value" : "success",
            "result" : {"consent_form_required" : session_player.consent_form_required}}