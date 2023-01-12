'''
admin interface
'''
from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ngettext

from main.forms import ParametersForm
from main.forms import SessionFormAdmin
from main.forms import InstructionFormAdmin
from main.forms import InstructionSetFormAdmin

from main.models import Parameters
from main.models import ParameterSet
from main.models import ParameterSetPlayer
from main.models import ParameterSetPeriod

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat
from main.models import SessionPlayerPeriod

from main.models import  HelpDocs

from main.models import HelpDocSubjectSet
from main.models import HelpDocSubject

from main.models.instruction_set import InstructionSet
from main.models.instruction import Instruction
from main.models.session_period import SessionPeriod

admin.site.site_header = settings.ADMIN_SITE_HEADER

@admin.register(HelpDocSubject)
class HelpDocSubjectAdmin(admin.ModelAdmin):
    fields = ['title','text']

class HelpDocSubectInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False

    model = HelpDocSubject
    fields = ['text']

@admin.register(HelpDocSubjectSet)
class HelpDocSubjectSetAdmin(admin.ModelAdmin):

    fields = ['label']
    actions = ['setup','duplicate_set']
    inlines = [HelpDocSubectInline]

    @admin.action(description='Initialize Help Docs')
    def setup(self, request, queryset):
        for v in queryset:
            v.setup()
        
        self.message_user(request, ngettext(
            '%d help doc set is initialized.',
            '%d help doc sets are initialized.',
            queryset.count(),
        ) % queryset.count(), messages.SUCCESS)
    
    @admin.action(description='Duplicate Set')
    def duplicate_set(self, request, queryset):
            '''
            duplicate help doc set
            '''
            if queryset.count() != 1:
                  self.message_user(request,"Select only one help doc set to copy.", messages.ERROR)
                  return

            base_help_doc_set = queryset.first()

            help_doc_set = HelpDocSubjectSet()
            help_doc_set.label = f"Copy of '{base_help_doc_set.label}'"
            help_doc_set.save()
            help_doc_set.copy_pages(base_help_doc_set.help_docs_subject)

            self.message_user(request,f'{base_help_doc_set} has been duplicated', messages.SUCCESS)

@admin.register(Parameters)
class ParametersAdmin(admin.ModelAdmin):
    '''
    parameters model admin
    '''
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    form = ParametersForm

    actions = []

@admin.register(ParameterSetPlayer)
class ParameterSetPlayerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['parameter_set']

class ParameterSetPlayerInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = ParameterSetPlayer
    fields = ['id_label', 'display_color']
    readonly_fields = ['id_label', 'display_color']

@admin.register(ParameterSetPeriod)
class ParameterSetPeriodAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['parameter_set', 'period_number']

class ParameterSetPeriodInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = ParameterSetPeriod
    fields = ['period_type', 'minimum_wrist_minutes', 'pay_block']
    readonly_fields = ['period_type', 'pay_block']

@admin.register(ParameterSet)
class ParameterSetAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = []
    inlines = [ParameterSetPeriodInline, ParameterSetPlayerInline]
    
class SessionPlayerPeriodInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = SessionPlayerPeriod
    fields = ['check_in', 'survey_complete', 'zone_minutes', 'earnings_individual', 'earnings_group']
    readonly_fields = ['check_in', 'survey_complete', 'zone_minutes', 'earnings_individual', 'earnings_group']

@admin.register(SessionPlayerPeriod)
class SessionPlayerPeriodAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['session_period', 'session_player']

@admin.register(SessionPlayerChat)
class SessionPlayerChatAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = []

class SessionPlayerInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = SessionPlayer
    fields = ['player_number', 'name' , 'email']
    readonly_fields = ['player_number', 'name' , 'email']

@admin.register(SessionPlayer)
class SessionPlayerAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['session', 'parameter_set_player', 'player_number']
    inlines = [SessionPlayerPeriodInline, ]

class sessionPeriodInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = SessionPeriod

@admin.register(SessionPeriod)
class SessionPeriodAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    readonly_fields = []


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    form = SessionFormAdmin

    inlines = [SessionPlayerInline, sessionPeriodInline]
    readonly_fields = ['parameter_set',]

#instruction set page
class InstructionPageInline(admin.TabularInline):
      '''
      instruction page admin screen
      '''
      extra = 0  
      form = InstructionFormAdmin
      model = Instruction
      can_delete = True

@admin.register(InstructionSet)
class InstructionSetAdmin(admin.ModelAdmin):
    form = InstructionSetFormAdmin

    def duplicate_set(self, request, queryset):
            '''
            duplicate instruction set
            '''
            if queryset.count() != 1:
                  self.message_user(request,"Select only one instruction set to copy.", messages.ERROR)
                  return

            base_instruction_set = queryset.first()

            instruction_set = InstructionSet()
            instruction_set.save()
            instruction_set.copy_pages(base_instruction_set.instructions)

            self.message_user(request,f'{base_instruction_set} has been duplicated', messages.SUCCESS)

    duplicate_set.short_description = "Duplicate Instruction Set"

    inlines = [
        InstructionPageInline,
      ]
    
    actions = [duplicate_set]

admin.site.register(HelpDocs)