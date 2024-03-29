'''
 staff page, edit name etc form
'''

from django import forms

class StaffEditNameEtcForm(forms.Form):
    '''
    staff page, edit name etc form
    '''
    name = forms.CharField(label='Full Name',
                           required=False,
                           widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.name",}))

    student_id = forms.CharField(label='Student ID',
                                 required=False,
                                 widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.student_id",}))

    email =  forms.EmailField(label='Email',
                              required=False,
                              widget=forms.EmailInput(attrs={"v-model":"staffEditNameEtcForm.email",}))
    
    note =  forms.CharField(label='Note',
                            required=False,
                            widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.note",}))
    
    group_number = forms.IntegerField(label='Group Number',
                                      widget=forms.NumberInput(attrs={"v-model":"staffEditNameEtcForm.group_number",
                                                                      "step":"1",}))
    
    fitbit_user_id = forms.CharField(label='Fitbit User ID',
                                     required=False,
                                     widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.fitbit_user_id",}))

    disabled = forms.ChoiceField(label='Active',
                                 choices=((1, 'No'), (0,'Yes')),
                                 widget=forms.Select(attrs={"v-model" : "staffEditNameEtcForm.disabled"}))
