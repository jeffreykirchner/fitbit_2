'''
instruction set
'''

#import logging

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_init

import main

class HelpDocSubjectSet(models.Model):
    '''
    instruction set model
    '''

    label = models.CharField(max_length = 100, default="Name Here", verbose_name="Label")                 #label text
        
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        
        verbose_name = 'Help Doc Subject Set'
        verbose_name_plural = 'Help Doc Subject Sets'
        ordering = ['label']
        constraints = [
            models.UniqueConstraint(fields=['label', ], name='unique_help_doc_subject_set'),
        ]

    def copy_pages(self, hd_set):
        '''
        copy instruction pages
        '''

        self.help_docs_subject.all().delete()
        
        #session player periods
        help_docs_subject = []

        for i in hd_set.all():
            help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title=i.title, text=i.text))
        
        main.models.HelpDocSubject.objects.bulk_create(help_docs_subject)
    
    def setup(self):

        self.help_docs_subject.all().delete()

        help_docs_subject = []

        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject check in help fixed pay", text="Checkin help text here: fixed pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject check in help group pay", text="Checkin help text here: group pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject check in help individual pay", text="Checkin help text here: individual pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject check in help no pay", text="Checkin help text here: no pay"))

        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject graph help fixed pay", text="Graph help text here: fixed pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject graph help group pay", text="Graph help text here: group pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject graph help individual pay", text="Graph help text here: individual pay"))
        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject graph help no pay", text="Graph help text here: no pay"))

        help_docs_subject.append(main.models.HelpDocSubject(help_doc_subject_set=self, title="Subject chat Help", text="Chat help text here."))

        main.models.HelpDocSubject.objects.bulk_create(help_docs_subject)
        
    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "label" : self.label,
            "help_docs_subject" : [i.json() for i in self.help_docs_subject.all()],
        }
    
    #return json object of class
    def json_min(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,        

            "label" : self.label,
        }
    
        
        