'''
Parameterset edit form
'''

from tinymce.widgets import TinyMCE

from django import forms

from main.models import ParameterSet
from main.globals import ColorAssignmentType

import  main

class ParameterSetForm(forms.ModelForm):
    '''
    Parameterset edit form
    '''    
    graph_y_max = forms.IntegerField(label='Graph: Max Y Value',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set.graph_y_max",
                                                                      "step":"1",
                                                                      "min":"1"}))
    
    group_size = forms.IntegerField(label='Group Size',
                                    min_value=1,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set.group_size",
                                                                    "step":"1",
                                                                    "min":"1"}))
    
    color_assignment_type = forms.ChoiceField(label='Color Assignment Type',
                                              choices=ColorAssignmentType.choices,
                                              widget=forms.Select(attrs={"v-model":"current_parameter_set.color_assignment_type",}))
                                       
    enable_chat = forms.ChoiceField(label='Enable Chat',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set.enable_chat",}))

    consent_form_required = forms.ChoiceField(label='Consent Form Required',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set.consent_form_required",}))

    consent_form = forms.CharField(label='Consent Form File Name',
                                   widget=forms.TextInput(attrs={"v-model":"current_parameter_set.consent_form",
                                                          }))


    show_instructions = forms.ChoiceField(label='Show Instructions',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set.show_instructions",}))
    
    instruction_set = forms.ModelChoiceField(label='Instruction Set',
                                            empty_label=None,
                                            queryset=main.models.InstructionSet.objects.all(),
                                            widget=forms.Select(attrs={"v-model":"current_parameter_set.instruction_set.id"}))
    
    help_doc_subject_set = forms.ModelChoiceField(label='Subject Help Docs',                                            
                                            queryset=main.models.HelpDocSubjectSet.objects.all(),
                                            widget=forms.Select(attrs={"v-model":"current_parameter_set.help_doc_subject_set.id"}))

    completion_message = forms.CharField(label='End of Study Message',
                                  required=False,
                                  widget=TinyMCE(attrs={"rows":10, "cols":100,"v-model":"current_parameter_set.completion_message"}))
    
    age_warning = forms.IntegerField(label='Age Warning',
                                    min_value=1,
                                    max_value=125,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set.age_warning",
                                                                    "step":"1",
                                                                    "min":"1"}))

    reconnection_limit = forms.IntegerField(label='Re-connection Limit',
                                    min_value=1,
                                    widget=forms.NumberInput(attrs={"v-model":"current_parameter_set.reconnection_limit",
                                                                    "step":"1",
                                                                    "min":"1"}))

    test_mode = forms.ChoiceField(label='Test Mode',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set.test_mode",}))

    class Meta:
        model=ParameterSet
        fields =['graph_y_max', 'group_size', 'color_assignment_type', 'enable_chat', 'consent_form_required',
                 'consent_form', 'show_instructions', 'instruction_set', 'help_doc_subject_set',
                 'test_mode' ,'completion_message', 'age_warning' ,'reconnection_limit']
