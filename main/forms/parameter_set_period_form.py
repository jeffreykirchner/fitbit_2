'''
parameterset player edit form
'''
from tinymce.widgets import TinyMCE

from django import forms

from main.models import ParameterSetPeriod

import main

class ParameterSetPeriodForm(forms.ModelForm):
    '''
    parameterset period edit form
    '''

    survey_link = forms.CharField(label='Survey Link',
                                  required=False,
                                  widget=forms.TextInput(attrs={"v-model" : "current_parameter_set_period.survey_link"}))

    survey_required = forms.ChoiceField(label='Enable Survey',
                                        choices=((1, 'Yes'), (0,'No')),
                                        widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.survey_required"}))
    
    minimum_wrist_minutes = forms.IntegerField(label="Minimum Wrist Minutes",
                                      min_value=0,
                                      max_value=1440,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.minimum_wrist_minutes",
                                                                      "step":"1",
                                                                      "min":"0",
                                                                      "max":"1440"}))
    
    show_notice = forms.ChoiceField(label='Show Notice',
                                        choices=((1, 'Yes'), (0,'No')),
                                        widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.show_notice"}))
    
    notice_text = forms.CharField(label='Notice Text',
                                  required=False,
                                  widget=TinyMCE(attrs={"rows":20, "cols":100,"v-model":"current_parameter_set_period.notice_text"}))
    
    show_graph_1 = forms.ChoiceField(label='Show Back Graph',
                                   choices=((1, 'Yes'), (0,'No')),
                                   widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.show_graph_1"}))

                        
    graph_1_start_period_number = forms.IntegerField(label="Back Graph Start Day",
                                                   min_value=1,
                                                   widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_1_start_period_number",
                                                                                   "step":"1",
                                                                                   "min":"1"}))                                                           

    graph_1_end_period_number = forms.IntegerField(label="Back Graph End Day",
                                                 min_value=1,
                                                 widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_1_end_period_number",
                                                                                 "step":"1",
                                                                                 "min":"1"}))
    
    show_graph_2 = forms.ChoiceField(label='Show Front Graph',
                                   choices=((1, 'Yes'), (0,'No')),
                                   widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.show_graph_2"}))

                        
    graph_2_start_period_number = forms.IntegerField(label="Front Graph Start Day",
                                                     min_value=1,
                                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_2_start_period_number",
                                                                                     "step":"1",
                                                                                     "min":"1"}))                                                           

    graph_2_end_period_number = forms.IntegerField(label="Front Graph End Day",
                                                   min_value=1,
                                                   widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_2_end_period_number",
                                                                                   "step":"1",
                                                                                   "min":"1"}))
    
    # pay_block = forms.IntegerField(label="Payment Block",
    #                                min_value=1,
    #                                widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.pay_block",
    #                                                                "step":"1",
    #                                                                "min":"1"}))

    parameter_set_pay_block = forms.ModelChoiceField(label='Pay Block',          
                                   empty_label=None,                          
                                   queryset=main.models.ParameterSetPayBlock.objects.none(),
                                   widget=forms.Select(attrs={"v-model":"current_parameter_set_period.parameter_set_pay_block.id"}))

    class Meta:
        model=ParameterSetPeriod
        fields =[ 'minimum_wrist_minutes', 'survey_required', 'survey_link',  
                 'show_notice', 'notice_text',  
                 'show_graph_1', 'graph_1_start_period_number', 'graph_1_end_period_number',
                 'show_graph_2', 'graph_2_start_period_number', 'graph_2_end_period_number', 
                 'parameter_set_pay_block']
    
    def clean_survey_link(self):
        
        try:
           survey_link = self.data.get('survey_link')
           survey_required = self.data.get('survey_required')

           if survey_required == 1 and not "http" in survey_link:
               raise forms.ValidationError('Invalid link')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return survey_link
    
    def clean_graph_1_end_period_number(self):
        
        try:
           graph_1_start_period_number = self.data.get('graph_1_start_period_number')
           graph_1_end_period_number = self.data.get('graph_1_end_period_number')
          
           if graph_1_start_period_number >  graph_1_end_period_number:
               raise forms.ValidationError('Must be >= graph 1 start period.')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return graph_1_end_period_number
    
    def clean_graph_2_end_period_number(self):
        try:
           graph_1_start_period_number = self.data.get('graph_1_start_period_number')
           graph_1_end_period_number = self.data.get('graph_1_end_period_number')

           graph_2_start_period_number = self.data.get('graph_2_start_period_number')
           graph_2_end_period_number = self.data.get('graph_2_end_period_number')

           show_graph_2 = self.data.get('show_graph_2')
          
           if graph_2_start_period_number >  graph_2_end_period_number:
               raise forms.ValidationError('Must be >= graph 2 start period.')
            
           if show_graph_2 == 1:
               if graph_1_end_period_number-graph_1_start_period_number != graph_2_end_period_number-graph_2_start_period_number:
                   raise forms.ValidationError('Graph ranges must match.')

        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return graph_2_end_period_number

    
