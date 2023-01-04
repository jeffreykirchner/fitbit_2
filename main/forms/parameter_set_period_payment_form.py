'''
parameterset period payment form
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

    no_pay_percent = forms.IntegerField(label="No Pay Fitbit Percent",
                                        min_value=0,
                                        max_value=100,
                                        widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_period_payment.no_pay_percent",
                                                                        "step":"1",
                                                                        "max":"100",
                                                                        "min":"0"}))


    class Meta:
        model=ParameterSetPeriodPayment
        fields =['payment', 'group_bonus', 'no_pay_percent']
    
    
