'''
websocket session list
'''
from decimal import Decimal, DecimalException

from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm
from main.forms import ParameterSetForm
from main.forms import ParameterSetPlayerForm
from main.forms import ParameterSetPeriodForm
from main.forms import ParameterSetPeriodPaymentForm
from main.forms import ParameterSetZoneMinutesForm
from main.forms import ParameterSetPayBlockForm
from main.forms import ParameterSetPayBlockPaymentForm

from main.models import Session
from main.models import ParameterSetPlayer
from main.models import ParameterSetPeriod
from main.models import ParameterSetPeriodPayment
from main.models import ParameterSetZoneMinutes
from main.models import ParameterSetPayBlock
from main.models import ParameterSetPayBlockPayment

import main

class StaffSessionParametersConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        #build response
        message_data = {}
        message_data["session"] = await sync_to_async(get_session)(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
    
    async def update_parameterset(self, event):
        '''
        update a parameterset
        '''
        #build response
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_parameterset_player(self, event):
        '''
        update a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_player)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 

    async def remove_parameterset_player(self, event):
        '''
        remove a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_remove_parameterset_player)(event["message_text"])

        message = {}
        message["messageType"] = "remove_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))   
    
    async def add_parameterset_player(self, event):
        '''
        add a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_player)(event["message_text"])

        message = {}
        message["messageType"] = "add_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def add_parameterset_period(self, event):
        '''
        add a parameterset period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_period)(event["message_text"])

        message = {}
        message["messageType"] = "add_parameterset_period"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_period(self, event):
        '''
        update a parameterset period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_period)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_period"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_period_payment(self, event):
        '''
        update a parameterset period payment
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_period_payment)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_period_payment"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_period_copy_forward(self, event):
        '''
        update a parameterset period copy forward
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_period_copy_forward)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_period_copy_forward"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_period_copy_previous(self, event):
        '''
        update a parameterset period copy previous
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_period_copy_previous)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_period_copy_previous"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def add_parameterset_zone_minutes(self, event):
        '''
        add a parameterset zone minutes
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_zone_minutes)(event["message_text"])

        message = {}
        message["messageType"] = "add_parameterset_zone_minutes"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_zone_minutes(self, event):
        '''
        update a parameterset zone minutes
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_zone_minutes)(event["message_text"])

        message = {}
        message["messageType"] = "update_parameterset_zone_minutes"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
  
    async def import_parameters(self, event):
        '''
        import parameters from another session
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_import_parameters)(event["message_text"])

        message_data["session"] = await sync_to_async(get_session)(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "import_parameters"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_parameters(self, event):
        '''
        download parameters to a file
        '''
        #download parameters to a file
        message = {}
        message["messageType"] = "download_parameters"
        message["messageData"] = await sync_to_async(take_download_parameters)(event["message_text"])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    #consumer updates
    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info("Connection update")

    async def add_parameterset_pay_block(self, event):
        '''
        add a parameterset pay block
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_pay_block)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_pay_block(self, event):
        '''
        update a parameterset pay block
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_pay_block)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def copy_previous_parameterset_pay_block(self, event):
        '''
        copy previous a parameterset pay block
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_copy_previous_parameterset_pay_block)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def copy_forward_parameterset_pay_block(self, event):
        '''
        copy forward a parameterset pay block
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_copy_forward_parameterset_pay_block)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_pay_block_payment(self, event):
        '''
        update a parameterset pay block payment
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_pay_block_payment)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def add_parameterset_pay_block_payment(self, event):
        '''
        add a parameterset pay block payment
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_parameterset_pay_block_payment)(event["message_text"])

        message = {}
        message["messageType"] = "update_pay_block"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

def get_session(id_):
    '''
    return session with specified id
    param: id_ {int} session id
    '''
    session = None
    logger = logging.getLogger(__name__)

    try:        
        session = Session.objects.get(id=id_)
        return session.json_for_parameter_set()
    except ObjectDoesNotExist:
        logger.warning(f"get_session session, not found: {id_}")
        return {}
        
def take_update_parameterset(data):
    '''
    update parameterset
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return
            
    form_data_dict = form_data
    form_data_dict["instruction_set"] = form_data_dict["instruction_set"]["id"]
    form_data_dict["help_doc_subject_set"] = form_data_dict["help_doc_subject_set"]["id"]

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    form = ParameterSetForm(form_data_dict, instance=session.parameter_set)

    if form.is_valid():
        #print("valid form")                
        form.save()    

        session.auto_assign_groups()
        session.parameter_set.update_json_local()

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid paramterset form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_player(data):
    '''
    update parameterset player
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]

    session = Session.objects.get(id=session_id)

    try:        
        parameter_set_player = ParameterSetPlayer.objects.get(id=form_data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_type paramterset_player, not found ID: {form_data['id']}")
        return
    
    form_data_dict = form_data

    form = ParameterSetPlayerForm(form_data_dict, instance=parameter_set_player)

    if form.is_valid():
                 
        form.save()
        session.parameter_set.update_json_fk(update_players=True)             

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_remove_parameterset_player(data):
    '''
    remove the specifed parmeterset player
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset player: {data}")

    session_id = data["sessionID"]
    increment_player = int(data["increment_player"])

    try:        
        session = Session.objects.get(id=session_id)

        for i in range(increment_player):
            if session.parameter_set.parameter_set_players.count()>1:
                session.parameter_set.parameter_set_players.last().delete()

        session.update_player_count()
        session.parameter_set.update_json_fk(update_players=True)
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player paramterset_player, not found")
        return
    
    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_add_parameterset_player(data):
    '''
    add a new parameter player to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset player: {data}")

    session_id = data["sessionID"]
    increment_player = int(data["increment_player"])

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return

    for i in range(increment_player):
        session.parameter_set.add_new_player()

    session.update_player_count()
    session.auto_assign_groups()
    session.parameter_set.update_json_fk(update_players=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_add_parameterset_period(data):
    '''
    add a new parameter set period
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset period: {data}")

    session_id = data["sessionID"]
    value = data["value"]
    increment_period = int(data["increment_period"])

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return

    for i in range(increment_period):
        if value == 1:
            session.parameter_set.add_new_period()
        elif session.parameter_set.parameter_set_periods.count()>1:
            session.parameter_set.parameter_set_periods.last().delete()
    
    session.update_end_date()
    session.parameter_set.update_json_fk(update_periods=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_update_parameterset_period(data):
    '''
    update parameterset period
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset period: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_period = ParameterSetPeriod.objects.get(id=form_data["id"])
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_period paramterset_period, not found ID: {form_data['id']}")
        return

    form_data['parameter_set_pay_block'] = form_data['parameter_set_pay_block']['id']

    form = ParameterSetPeriodForm(form_data, instance=parameter_set_period)
    form.fields['parameter_set_pay_block'].queryset = session.parameter_set.parameter_set_pay_blocks_a.all()

    if form.is_valid():
        #print("valid form")             
        form.save()              

        session.parameter_set.update_json_fk(update_periods=True)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset period form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_period_copy_forward(data):
    '''
    update parameterset period copy forward
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset period copy forward: {data}")

    session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    try:        
        parameter_set_period = ParameterSetPeriod.objects.get(id=data["id"])
        
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_period paramterset_period, not found ID: {data['id']}")
        return

    parameter_set_period_list = parameter_set_period.parameter_set.parameter_set_periods.filter(period_number__gt=parameter_set_period.period_number)    

    for p in parameter_set_period_list:
        p.copy_forward(parameter_set_period)
   
    session.parameter_set.update_json_fk(update_periods=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      

def take_update_parameterset_period_copy_previous(data):
    '''
    copy previous parameterset period to this one
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset period copy previous: {data}")

    session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    try:        
        parameter_set_period = ParameterSetPeriod.objects.get(id=data["id"])
        
    except ObjectDoesNotExist:
        logger.warning(f"update_parameterset_period_copy_previous paramterset_period, not found ID: {data['id']}")
        return

    parameter_set_period_previous = parameter_set_period.parameter_set.parameter_set_periods.filter(period_number=parameter_set_period.period_number-1).first()

    if parameter_set_period:  
        parameter_set_period.copy_forward(parameter_set_period_previous)
    else:
         logger.warning(f"update_parameterset_period_copy_previous paramterset_period, no prevous period ID: {data['id']}")
   
    session.parameter_set.update_json_fk(update_periods=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_update_parameterset_period_payment(data):
    '''
    update parameterset period payment
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset period payment: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_period_payment = ParameterSetPeriodPayment.objects.get(id=form_data["id"])
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_period_payment paramterset_period_payment, not found ID: {form_data['id']}")
        return

    form = ParameterSetPeriodPaymentForm(form_data, instance=parameter_set_period_payment)
   
    if form.is_valid():
        #print("valid form")             
        form.save()              

        session.parameter_set.update_json_fk(update_periods=True)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset period payment form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_add_parameterset_zone_minutes(data):
    '''
    add a new parameter set zone minutes
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset zone minutes: {data}")

    session_id = data["sessionID"]
    value = data["value"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return

    if value == 1:
        session.parameter_set.add_new_zone_minutes()
    elif session.parameter_set.parameter_set_zone_minutes.count()>1:
        session.parameter_set.parameter_set_zone_minutes.first().delete()

    session.parameter_set.update_json_fk(update_zone_minutes=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_update_parameterset_zone_minutes(data):
    '''
    update parameterset zone minutes
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset zone minutes: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_zone_minutes = ParameterSetZoneMinutes.objects.get(id=form_data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_zone_minutes paramterset_period, not found ID: {form_data['id']}")
        return

    form = ParameterSetZoneMinutesForm(form_data, instance=parameter_set_zone_minutes)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        session = Session.objects.get(id=session_id)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_add_parameterset_pay_block(data):
    '''
    add a new parameter set pay block
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset pay block: {data}")

    session_id = data["sessionID"]
    value = data["value"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_parameterset_pay_block session, not found ID: {session_id}")
        return

    if value == 1:
        session.parameter_set.add_new_pay_block()
    elif session.parameter_set.parameter_set_pay_blocks_a.count() > 1:
        session.parameter_set.parameter_set_pay_blocks_a.last().delete()

    session.parameter_set.update_json_fk(update_pay_blocks=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_update_parameterset_pay_block(data):
    '''
    update parameterset pay block
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset pay block: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_pay_block = ParameterSetPayBlock.objects.get(id=form_data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_pay_block , not found ID: {form_data['id']}")
        return

    form = ParameterSetPayBlockForm(form_data, instance=parameter_set_pay_block)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        session = Session.objects.get(id=session_id)
        session.parameter_set.update_json_fk(update_pay_blocks=True)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_copy_previous_parameterset_pay_block(data):
    '''
    copy previous parameterset pay block
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Copy previous parameterset pay block: {data}")

    session_id = data["sessionID"]
    payblock_id = data["payblockID"]

    try:        
        parameter_set_pay_block = ParameterSetPayBlock.objects.get(id=payblock_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_copy_previous_parameterset_pay_block , not found ID: {payblock_id}")
        return     

    session = Session.objects.get(id=session_id)

    if parameter_set_pay_block.pay_block_number>1:
        parameter_set_pay_block_source = session.parameter_set.parameter_set_pay_blocks_a.all().get(pay_block_number=parameter_set_pay_block.pay_block_number-1)
        parameter_set_pay_block.from_dict(parameter_set_pay_block_source.json(), False)        

    session.parameter_set.update_json_fk(update_pay_blocks=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}       

def take_copy_forward_parameterset_pay_block(data):
    '''
    copy forward parameterset pay block
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Copy forward parameterset pay block: {data}")

    session_id = data["sessionID"]
    payblock_id = data["payblockID"]

    try:        
        parameter_set_pay_block = ParameterSetPayBlock.objects.get(id=payblock_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_copy_forward_parameterset_pay_block , not found ID: {payblock_id}")
        return         

    session = Session.objects.get(id=session_id)

    parameter_set_pay_block_targets = session.parameter_set.parameter_set_pay_blocks_a.filter(pay_block_number__gt=parameter_set_pay_block.pay_block_number)

    temp_j = parameter_set_pay_block.json()

    for p in parameter_set_pay_block_targets:
        p.from_dict(temp_j, False) 

    session.parameter_set.update_json_fk(update_pay_blocks=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}              
                            
def take_update_parameterset_pay_block_payment(data):
    '''
    update parameterset pay block payment
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset pay block payment: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_pay_block_payment = ParameterSetPayBlockPayment.objects.get(id=form_data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_pay_block_payment , not found ID: {form_data['id']}")
        return

    form = ParameterSetPayBlockPaymentForm(form_data, instance=parameter_set_pay_block_payment)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        session = Session.objects.get(id=session_id)
        session.parameter_set.update_json_fk(update_pay_blocks=True)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_pay_block_payment(data):
    '''
    update parameterset pay block payment
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset pay block payment: {data}")

    session_id = data["sessionID"]
    # paramterset_period_id = data["paramterset_period_id"]
    form_data = data["formData"]

    try:        
        parameter_set_pay_block_payment = ParameterSetPayBlockPayment.objects.get(id=form_data["id"])
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_pay_block_payment , not found ID: {form_data['id']}")
        return

    form = ParameterSetPayBlockPaymentForm(form_data, instance=parameter_set_pay_block_payment)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        session = Session.objects.get(id=session_id)
        session.parameter_set.update_json_fk(update_pay_blocks=True)

        return {"value" : "success", "parameter_set" : session.parameter_set.json()}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_add_parameterset_pay_block_payment(data):
    '''
    add a new parameter set pay block
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset pay block: {data}")

    session_id = data["sessionID"]
    pay_block_id = data["payblockID"]
    value = data["value"]

    try:        
        pay_block = ParameterSetPayBlock.objects.get(id=pay_block_id)
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_add_parameterset_pay_block_payment session, not found ID: {pay_block_id}")
        return

    if value == 1:
        pay_block.add_pay_block_payment()
    elif pay_block.parameter_set_pay_block_payments_a.count() > 0:
        pay_block.parameter_set_pay_block_payments_a.first().delete()

    pay_block.parameter_set.update_json_fk(update_pay_blocks=True)

    return {"value" : "success", "parameter_set" : session.parameter_set.json()}

def take_import_parameters(data):
    '''
    import parameters from another session
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Import parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]
    
    form_data_dict = form_data

    if not form_data_dict["session"]:
        return {"status" : "fail", "message" :  "Invalid session."}

    # for field in form_data:            
    #     form_data_dict[field["name"]] = field["value"]

    source_session = Session.objects.get(id=form_data_dict["session"])
    target_session = Session.objects.get(id=session_id)

    status = target_session.parameter_set.from_dict(source_session.parameter_set.json()) 
    target_session.update_player_count()
    target_session.update_end_date()

    target_session.auto_assign_groups()

    return status      

def take_download_parameters(data):
    '''
    download parameters to a file
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Download parameters: {data}")

    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)
   
    return {"status" : "success", "parameter_set":session.parameter_set.json()}                      