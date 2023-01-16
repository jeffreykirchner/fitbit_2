'''
parameterset player 
'''

from django.db import models

from main.models import ParameterSet

import main

class ParameterSetPlayer(models.Model):
    '''
    paramterset player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_players")

    id_label = models.CharField(verbose_name='ID Label', max_length = 10, default="1")      #id label shown on screen to subjects
    display_color = models.CharField(max_length = 300, default = '#000000', verbose_name = 'Graph Color')  

    timestamp = models.DateTimeField(auto_now_add= True)
    updated = models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering=['id']

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of parameterset player
        '''

        self.id_label = source.get("id_label")
        self.display_color = source.get("display_color")

        self.save()
        
        message = "Parameters loaded successfully."

        return message
    
    def label_html(self):
        '''
        return label in html format
        '''

        return f"""<span style='color:{self.display_color}'>{self.id_label}</span>"""

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "display_color" : self.display_color,
        }
    
    def json_for_subject(self):
        '''
        return json object for subject screen
        '''

        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "display_color" : self.display_color,

        }


