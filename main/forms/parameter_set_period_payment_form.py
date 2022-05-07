'''
parameterset player edit form
'''

from django import forms

from main.models import ParameterSetPeriodPayment

from main.globals import PeriodType

class ParameterSetPeriodPaymentForm(forms.ModelForm):
    '''
    parameterset period payment edit form
    '''

    payment = forms.DecimalField(label='Individual Payment',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period_payment.payment",
                                                                     "step":"0.01"}))
    group_bonus = forms.DecimalField(label='Group Bonus',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period_payment.group_bonus",
                                                                     "step":"0.01"}))

    class Meta:
        model=ParameterSetPeriodPayment
        fields =['payment', 'group_bonus']
    
    
