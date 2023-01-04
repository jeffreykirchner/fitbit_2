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

    class Meta:
        model = ParameterSetPayBlock
        fields = ['pay_block_type',]
    
   
    
