'''
parameterset player edit form
'''

from django import forms

from main.models import ParameterSetPeriod

from main.globals import PeriodType

class ParameterSetPeriodForm(forms.ModelForm):
    '''
    parameterset player edit form
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

    class Meta:
        model=ParameterSetPeriod
        fields =['survey_link', 'survey_required', 'period_type']
    

    def clean_survey_link(self):
        
        try:
           survey_link = self.data.get('survey_link')
           survey_required = self.data.get('survey_required')

           if survey_required == 1 and not "http" in survey_link:
               raise forms.ValidationError('Invalid link')
            
        except ValueError:
            raise forms.ValidationError('Invalid Entry')

        return survey_link
    
