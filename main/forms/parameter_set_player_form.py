'''
parameterset player edit form
'''

from django import forms
from django.db.models.query import RawQuerySet

from main.models import ParameterSetPlayer

class ParameterSetPlayerForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    id_label = forms.CharField(label='Label Used in Chat',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.id_label",}))
    
    display_color = forms.CharField(label='Graph Color',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.display_color",}))

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'display_color']
    
