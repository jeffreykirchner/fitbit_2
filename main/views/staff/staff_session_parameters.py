'''
staff view
'''
import logging
import json
import uuid

from django.views import View
from django.shortcuts import render
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from main.decorators import user_is_owner

from main.models import Session

from main.forms import ImportParametersForm
from main.forms import ParameterSetForm
from main.forms import ParameterSetPlayerForm
from main.forms import ParameterSetPeriodForm
from main.forms import ParameterSetPayBlockForm
from main.forms import ParameterSetPayBlockPaymentForm

class StaffSessionParametersView(SingleObjectMixin, View):
    '''
    class based staff view
    '''
    template_name = "staff/staff_session_parameters.html"
    websocket_path = "staff-session-parameters"
    model = Session
    
    @method_decorator(user_is_owner)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''
        session = self.get_object()

        parameterset_player_form = ParameterSetPlayerForm()
        parameterset_period_form = ParameterSetPeriodForm()
        parameterset_pay_block_form = ParameterSetPayBlockForm()
        parameterset_pay_block_payment_form = ParameterSetPayBlockPaymentForm()

        form_ids=[]
        for i in ParameterSetForm():
            form_ids.append(i.html_name)

        for i in parameterset_player_form:
            form_ids.append(i.html_name)

        for i in parameterset_period_form:
            form_ids.append(i.html_name)
        
        for i in parameterset_pay_block_form:
           form_ids.append(i.html_name)

        for i in parameterset_pay_block_payment_form:
           form_ids.append(i.html_name)

        if session.parameter_set.parameter_set_players.count() == 0:
            session.parameter_set.add_new_player()
        
        if session.parameter_set.parameter_set_periods.count() == 0:
            session.parameter_set.add_new_period()
            
        parameterset_period_form.fields['parameter_set_pay_block'].queryset = session.parameter_set.parameter_set_pay_blocks_a.all()

        return render(request=request,
                      template_name=self.template_name,
                      context={"channel_key" : uuid.uuid4(),
                               "player_key" :  uuid.uuid4(),
                               "id" : session.id,
                               "parameter_set_form" : ParameterSetForm(),
                               "parameter_set_player_form" : parameterset_player_form,
                               "form_ids" : form_ids,
                               "parameterset_period_form" : parameterset_period_form,
                               "parameterset_pay_block_form" : parameterset_pay_block_form,
                               "parameterset_pay_block_payment_form" : parameterset_pay_block_payment_form,
                               "import_parameters_form" : ImportParametersForm(user=request.user,session_id=session.id),     
                               "websocket_path" : self.websocket_path,
                               "page_key" : f'{self.websocket_path}-{session.id}',
                               "session" : session,
                               })
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        '''
        handle post requests
        '''

        logger = logging.getLogger(__name__) 
        session = self.get_object()

        #check for file upload
        try:
            f = request.FILES['file']
        except Exception  as e: 
            logger.info(f'Staff_Session no file upload: {e}')
            f = -1
        
         #check for file upload
        if f != -1:
            return takeFileUpload(f, session)
        else:
            data = json.loads(request.body.decode('utf-8'))
        

        return JsonResponse({"response" :  "fail"},safe=False)

#take parameter file upload
def takeFileUpload(f, session):
    logger = logging.getLogger(__name__) 
    logger.info("Upload file")

    #format incoming data
    v=""

    for chunk in f.chunks():
        v += str(chunk.decode("utf-8-sig"))

    message = ""

    try:
        if v[0]=="{":
            return upload_parameter_set(v, session)
        else:
            message = "Invalid file format."
    except Exception as e:
        message = f"Failed to load file: {e}"
        logger.info(message)       

    return JsonResponse({"session" : session.json(),
                         "message" : message,
                                },safe=False)

#take parameter set to upload
def upload_parameter_set(v, session):
    logger = logging.getLogger(__name__) 
    logger.info("Upload parameter set")
    

    ps = session.parameter_set

    logger.info(v)
    v = eval(v.replace("null", "None"))
    #logger.info(v)       

    message = ps.from_dict(v)

    session.update_player_count()
    session.update_end_date()
    session.auto_assign_groups()

    return JsonResponse({"session" : session.json(),
                         "message" : message,
                                },safe=False)
