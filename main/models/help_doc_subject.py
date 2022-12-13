'''
help document
'''
from tinymce.models import HTMLField
from django.db import models

from main.models import HelpDocSubjectSet

class HelpDocSubject(models.Model):
    '''
    help document
    '''
    help_doc_subject_set = models.ForeignKey(HelpDocSubjectSet, on_delete=models.CASCADE, related_name="help_docs_subject")

    title = models.CharField(verbose_name = 'Title', max_length = 300, default="")    
    text = HTMLField(verbose_name = 'Help Doc Text', max_length = 100000, default="")

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    class Meta:
        verbose_name = 'Help Doc Subject'
        verbose_name_plural = 'Help Docs Subject'
        ordering = ['title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'help_doc_subject_set'], name='unique_help_doc_subject'),
        ]

    def __str__(self):
        return self.title
    
    def json(self):
        return{
            "id":self.id,
            "title":self.title,
            "text":self.text,
        }