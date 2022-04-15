'''
session edit form
'''

from django import forms

from main.models import Session

from django.contrib.admin.widgets import AdminDateWidget
from django.forms import DateInput, SelectDateWidget

class SessionForm(forms.ModelForm):
    '''
    session edit form
    '''
    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={"v-model":"session.title",
                                                           "v-on:keyup.enter":"sendUpdateSession()"}))

    start_date = forms.DateField(label="Start Date",
                                 error_messages={'invalid' : 'Format: M/D/YYYY'},
                                 widget=DateInput(attrs={"v-model" : "session.start_date_widget",
                                                         "type": "date",
                                                         "v-bind:disabled" : "session.started"}))

    class Meta:
        model=Session
        fields =['title', 'start_date']
