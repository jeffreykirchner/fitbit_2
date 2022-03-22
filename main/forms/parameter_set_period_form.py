'''
parameterset player edit form
'''
from tinymce.widgets import TinyMCE

from django import forms

from main.models import ParameterSetPeriod

from main.globals import PeriodType

class ParameterSetPeriodForm(forms.ModelForm):
    '''
    parameterset period edit form
    '''

    survey_link = forms.CharField(label='Link',
                                  required=False,
                                  widget=forms.TextInput(attrs={"v-model" : "current_parameter_set_period.survey_link"}))

    survey_required = forms.ChoiceField(label='Enable Survey',
                                        choices=((1, 'Yes'), (0,'No')),
                                        widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.survey_required"}))
    
    period_type = forms.ChoiceField(label='Period Type',
                                       choices=PeriodType.choices,
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set_period.period_type",}))
    
    minimum_wrist_minutes = forms.IntegerField(label="Yesterday's Minimum Wrist Minutes",
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
    
    show_graph = forms.ChoiceField(label='Show Graph',
                                   choices=((1, 'Yes'), (0,'No')),
                                   widget=forms.Select(attrs={"v-model" : "current_parameter_set_period.show_graph"}))

                        
    graph_start_period_number = forms.IntegerField(label="Graph Start Day",
                                                   min_value=1,
                                                   widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_start_period_number",
                                                                                    "step":"1",
                                                                                   "min":"1"}))                                                           

    graph_end_period_number = forms.IntegerField(label="Graph End Day",
                                                 min_value=1,
                                                 widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.graph_end_period_number",
                                                                                 "step":"1",
                                                                                 "min":"1"}))
    
    pay_block = forms.IntegerField(label="Payment Group",
                                   min_value=1,
                                   widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period.pay_block",
                                                                   "step":"1",
                                                                   "min":"1"}))

    class Meta:
        model=ParameterSetPeriod
        fields =['survey_link', 'survey_required', 'period_type', 'minimum_wrist_minutes', 'show_graph', 'graph_start_period_number', 'graph_end_period_number', 'pay_block', 'show_notice', 'notice_text']
    

    def clean_survey_link(self):
        
        try:
           survey_link = self.data.get('survey_link')
           survey_required = self.data.get('survey_required')

           if survey_required == 1 and not "http" in survey_link:
               raise forms.ValidationError('Invalid link')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return survey_link
    
    def clean_graph_end_period_number(self):
        
        try:
           graph_start_period_number = self.data.get('graph_start_period_number')
           graph_end_period_number = self.data.get('graph_end_period_number')
          
           if graph_start_period_number >  graph_end_period_number:
               raise forms.ValidationError('Must be >= graph start period.')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return graph_end_period_number
    
