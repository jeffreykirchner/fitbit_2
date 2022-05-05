'''
Parameterset edit form
'''

from django import forms

from main.models import ParameterSet

import  main

class ParameterSetForm(forms.ModelForm):
    '''
    Parameterset edit form
    '''    
    graph_y_max = forms.IntegerField(label='Graph: Max Y Value',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.graph_y_max",
                                                                      "step":"1",
                                                                      "min":"1"}))
                                       
    enable_chat = forms.ChoiceField(label='Enable Chat',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.enable_chat",}))

    consent_form_required = forms.ChoiceField(label='Consent Form Required',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.consent_form_required",}))

    consent_form = forms.CharField(label='Consent Form File Name',
                                   widget=forms.TextInput(attrs={"v-model":"session.parameter_set.consent_form",
                                                          }))


    show_instructions = forms.ChoiceField(label='Show Instructions',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.show_instructions",}))
    
    instruction_set = forms.ModelChoiceField(label='Instruction Set',
                                            empty_label=None,
                                            queryset=main.models.InstructionSet.objects.all(),
                                            widget=forms.Select(attrs={"v-model":"session.parameter_set.instruction_set.id"}))

    test_mode = forms.ChoiceField(label='Test Mode',
                                       choices=((True, 'Yes'), (False,'No' )),
                                       widget=forms.Select(attrs={"v-model":"session.parameter_set.test_mode",}))

    class Meta:
        model=ParameterSet
        fields =['graph_y_max', 'enable_chat', 'consent_form_required', 'consent_form', 'show_instructions', 'instruction_set', 'test_mode']
