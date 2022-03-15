'''
parameterset zone minutes edit form
'''

from django import forms

from main.models import ParameterSetZoneMinutes

class ParameterSetZoneMinutesForm(forms.ModelForm):
    '''
    parameterset zone minutes edit form
    '''

    label = forms.CharField(label='Label Displayed',
                            widget=forms.TextInput(attrs={"v-model":"current_parameter_set_zone_minutes.label",}))
    
    zone_minutes = forms.IntegerField(label='Zone Minutes',
                                      min_value=0,
                                      max_value=1440,
                                      widget=forms.NumberInput(attrs={"v-model":"current_parameter_set_zone_minutes.zone_minutes",
                                                                      "step":"1",
                                                                      "min":"0",
                                                                      "max":"1440"}))

    class Meta:
        model=ParameterSetZoneMinutes
        fields =['label', 'zone_minutes']
    
