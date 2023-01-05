'''
parameterset pay block form
'''

from django import forms

from main.models import ParameterSetPayBlock

from main.globals import PayBlockType

class ParameterSetPayBlockForm(forms.ModelForm):
    '''
    parameterset pay block form
    '''
    
    pay_block_type = forms.ChoiceField(label='Pay Block Type',
                                       choices=PayBlockType.choices,
                                       widget=forms.Select(attrs={"v-model":"current_parameter_set_pay_block.pay_block_type",}))

    fixed_pay = forms.DecimalField(label='Daily Fixed Payment',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block.fixed_pay",
                                                                     "step":"0.01"}))
    
    no_pay_percent = forms.DecimalField(label='Daily Fitbit Percent Earned',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block.no_pay_percent",
                                                                     "step":"0.01"}))

    class Meta:
        model = ParameterSetPayBlock
        fields = ['pay_block_type', 'fixed_pay', 'no_pay_percent']
    
   
    
