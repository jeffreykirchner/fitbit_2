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
    display_block = forms.IntegerField(label='Number of Periods in Graph',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.display_block",
                                                                      "step":"1",
                                                                      "min":"1"}))
    
    graph_y_max = forms.IntegerField(label='Graph: Max Y Value',
                                      min_value=1,
                                      widget=forms.NumberInput(attrs={"v-model":"session.parameter_set.graph_y_max",
                                                                      "step":"1",
                                                                      "min":"1"}))
                                       
    # enable_chat = forms.ChoiceField(label='Enable Chat',
    #                                    choices=((True, 'Yes'), (False,'No' )),
    #                                    widget=forms.Select(attrs={"v-model":"session.parameter_set.enable_chat",}))

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
        fields =['display_block', 'graph_y_max', 'show_instructions', 'instruction_set', 'test_mode'] #, 'enable_chat'
