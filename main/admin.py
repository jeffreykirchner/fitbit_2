'''
admin interface
'''
import datetime

from django.db.backends.postgresql.psycopg_any import DateTimeTZRange
from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ngettext
from django.utils import timezone

from main.forms import ParametersForm
from main.forms import SessionFormAdmin
from main.forms import InstructionFormAdmin
from main.forms import InstructionSetFormAdmin

from main.models import Parameters

from main.models import Profile
from main.models import ProfileLoginAttempt

from main.models import ParameterSet
from main.models import ParameterSetPlayer
from main.models import ParameterSetPeriod
from main.models import ParameterSetPayBlock
from main.models import ParameterSetPayBlockPayment

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

@admin.register(ParameterSetPayBlockPayment)
class ParameterSetPayblockPaymentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['parameter_set_pay_block']

class ParameterSetPayblockPaymentInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = ParameterSetPayBlockPayment
    fields = ['label', 'zone_minutes', 'payment', 'group_bonus' ,'no_pay_percent']

@admin.register(ParameterSetPayBlock)
class ParameterSetPayblockAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['parameter_set']
    inlines = [ParameterSetPayblockPaymentInline]

class ParameterSetPayblockInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = ParameterSetPayBlock
    fields = ['pay_block_type', 'pay_block_number', 'fixed_pay' ,'no_pay_percent']

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
    fields = [ 'minimum_wrist_minutes']
    readonly_fields = []

@admin.register(ParameterSet)
class ParameterSetAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = []
    inlines = [ParameterSetPeriodInline, ParameterSetPlayerInline, ParameterSetPayblockInline]
    
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
    
    readonly_fields = ['session_period', 'session_player' , 'last_login']

@admin.register(SessionPlayerChat)
class SessionPlayerChatAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
    
    readonly_fields = []

class SessionPlayerInline(admin.TabularInline):
    def has_add_permission(self, request, obj=None):
        return False
      
    def has_delete_permission(self, request, obj=None):
        return False
    
    show_change_link = True

    model = SessionPlayer
    fields = ['player_number', 'name' , 'email','note']
    readonly_fields = ['player_number']

@admin.register(SessionPlayer)
class SessionPlayerAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['session', 'parameter_set_player', 'player_number', 'player_key',
                       'player_key_backup' , 'fitbit_last_synced', 'fitbit_device', 'channel_name',
                       'recruiter_id_private' ,'recruiter_id_public', 'connecting']

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
    
    # def has_change_permission(self, request, obj=None):
    #     return False
    
    readonly_fields = []


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    
    def reset(self, request, queryset):

        for i in queryset.all():
            i.reset_experiment()

        self.message_user(request, ngettext(
                '%d session is reset.',
                '%d sessions are reset.',
                queryset.count(),
        ) % queryset.count(), messages.SUCCESS)
    
    def refresh(self, request, queryset):

        for i in queryset.all():
            i.parameter_set.json(update_required=True)

        self.message_user(request, ngettext(
                '%d session is refreshed.',
                '%d sessions are refreshed.',
                queryset.count(),
        ) % queryset.count(), messages.SUCCESS)
    
    form = SessionFormAdmin

    inlines = [SessionPlayerInline, sessionPeriodInline]
    readonly_fields = ['parameter_set',]
    list_display = ['title','creator']
    actions = ['reset', 'refresh']

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

@admin.register(ProfileLoginAttempt)
class ProfileLoginAttemptAdmin(admin.ModelAdmin):
    '''
    profile login attempt admin
    '''
    list_display = ['profile','success','timestamp','note']
    readonly_fields=['success', 'note','profile', 'success', 'timestamp', 'note']

    def has_add_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    
#profile login attempt inline
class ProfileLoginAttemptInline(admin.TabularInline):
      '''
      profile login attempt inline
      '''
    #   def get_queryset(self, request):
    #         qs = super().get_queryset(request)
            
    #         return qs.filter(timestamp__contained_by=DateTimeTZRange(timezone.now() - datetime.timedelta(days=30), timezone.now()))
      
      def has_add_permission(self, request, obj=None):
            return False

      def has_change_permission(self, request, obj=None):
            return False

      extra = 0  
      model = ProfileLoginAttempt
      can_delete = True
      
      fields=('id','success','note')
      readonly_fields = ('timestamp',)
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    '''
    profile admin
    '''

    ordering = ['user__last_name', 'user__first_name']
    search_fields = ['user__last_name', 'user__first_name', 'user__email']

    inlines = [ProfileLoginAttemptInline]