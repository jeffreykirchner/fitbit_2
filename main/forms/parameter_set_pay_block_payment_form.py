'''
parameterset pay block form
'''

from django import forms

from main.models import ParameterSetPayBlockPayment

class ParameterSetPayBlockPaymentForm(forms.ModelForm):
    '''
    parameterset pay block form
    '''

    label = forms.CharField(label='Label Displayed',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_pay_block_payment.label",}))

    zone_minutes = forms.IntegerField(label="Zone Minutes",
                                        min_value=0,
                                        widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block_payment.zone_minutes",
                                                                        "step":"1",
                                                                        "min":"0"}))
    
    payment = forms.DecimalField(label='Individual Payment',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block_payment.payment",
                                                                     "step":"0.01"}))
    group_bonus = forms.DecimalField(label='Group Bonus',
                                     min_value=0,
                                     widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block_payment.group_bonus",
                                                                     "step":"0.01"}))

    no_pay_percent = forms.IntegerField(label="No Pay Fitbit Percent",
                                        min_value=0,
                                        max_value=100,
                                        widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_pay_block_payment.no_pay_percent",
                                                                        "step":"1",
                                                                        "max":"100",
                                                                        "min":"0"}))

    class Meta:
        model = ParameterSetPayBlockPayment
        fields = ['label', 'zone_minutes', 'payment', 'group_bonus', 'no_pay_percent']
    
   
    
