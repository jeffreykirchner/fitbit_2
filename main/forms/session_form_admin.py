from django import forms
from main.models import Session
from django.contrib.auth.models import User
from django.forms import ModelChoiceField
from django.forms import ModelMultipleChoiceField
from main.globals import ExperimentPhase


class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email

class UserModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.email

class SessionFormAdmin(forms.ModelForm):

    creator =  UserModelChoiceField(label="Creator",
                                     empty_label=None,
                                     queryset=User.objects.all(),
                                     widget=forms.Select(attrs={}))
    
    collaborators = UserModelMultipleChoiceField(label="Collaborators",
                                                 queryset=User.objects.all(),
                                                 required=False
                                                   )

    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={"size":"50"}))

    
    shared = forms.BooleanField(label='Share parameterset with all.', required=False)
    locked = forms.BooleanField(label='Locked, prevent deletion.', required=False)
    soft_delete = forms.BooleanField(label='Soft Delete.', required=False)
    finished = forms.BooleanField(label='Finished.', required=False)
    current_experiment_phase = forms.ChoiceField(label='Current Experiment Phase',
                                                 choices=ExperimentPhase.choices,
                                                 widget=forms.Select(attrs={}))

    class Meta:
        model=Session
        fields = ('creator', 'collaborators', 'title', 'shared', 'locked', 'soft_delete', 'finished', 'current_experiment_phase', 'parameter_set')