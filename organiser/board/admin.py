from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core import urlresolvers
from django import forms
import datetime
from .models import Duty,Person,Patient,Volunteer,Category,Ward
import board.helpers as h
import board.validators as validators

from pprint import pprint


admin.site.site_header = _("Volunteer administration")
admin.site.site_title = _("Volunteer administration")


class PatientWardsFilter(admin.SimpleListFilter):
    title = _('wards')
    parameter_name = 'wards'

    def lookups(self, request, model_admin):
        return [(x.name, _(x.name)) for x in Ward.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ward__name = self.value())
        
class VolunteerCategoriesFilter(admin.SimpleListFilter):
    title = _('categories')
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        return [(x.name, _(x.name)) for x in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(availableCategories__name = self.value())


class VolunteerActiveFilter(admin.SimpleListFilter):
    title = _('active')
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (('active', _('Active')), 
                ('inactive', _('Inactive'))
            )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(active = True)
        elif self.value() == 'inactive':
            return queryset.filter(active = False)


class DutyFilter(admin.SimpleListFilter):
    title = _('duty')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'duty_soon'
    def lookups(self, request, model_admin):
        return ( ('today', _('Today')), ('week', _('Next 7 days')))

    def queryset(self, request, queryset):
        if self.value() == 'today':
            # for 'today' it is simple...
            return queryset.filter(date = now().date())

        if self.value() == 'week':
            future_date = (now() + datetime.timedelta(days=7)).date()
            return h.filter_date_range(
                    queryset,
                    'date',
                    now().date(),
                    future_date
                )

class BirthdayFilter(admin.SimpleListFilter):
    title = _('birthday')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'birthday_soon'
    def lookups(self, request, model_admin):
        return ( ('today', _('Today')), ('week', _('Next 7 days')))

    def queryset(self, request, queryset):
        # select by date... Patient.objects.filter(birthday__month=4, birthday__day=1)
        if self.value() == 'today':
            return queryset.filter(
                    birthday = h.bday(now=True)
                )
        if self.value() == 'week':
            future_date = (now() + datetime.timedelta(days=7)).date()
            return h.filter_date_range(
                    queryset,
                    'birthday',
                    h.bday(now=True),
                    h.bday(future_date.month, future_date.day)
                )

class DutyAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(DutyAdminForm, self).clean()
        volunteer = cleaned_data.get('volunteer')
        category = cleaned_data.get('category')
        validators.validate_duty_category(volunteer, category)
        return self.cleaned_data


class DutyAdmin(admin.ModelAdmin):
    form = DutyAdminForm
    fieldsets = [
       (_('Where'), {'fields': ['category']}),
       (_('Who'), {'fields': ['volunteer', 'patient']}),
       (_('When'), {'fields': ['date', 'time']}),
       (_('Other'), {'fields': ['notes']}),
    ]
    list_display = ('volunteer', 'patient',
            'date', 'time', 'category', 'notes')
    list_filter = [DutyFilter]


class VolunteerAdmin(admin.ModelAdmin):
    fieldsets = [
       (_('Person'), {'fields': ['pid', 'first_name', 'surname', 'birthdate']}),
       (_('Contact'), {'fields': ['email','phone1','phone2','address']}),
       (_('Other'), {'fields': ['professions','availableCategories', 'workingSince', 'workedUntil', 'active','notes']}),
    ]
    list_display = ('first_name', 'surname',
                    'birthdate', 'professions', 'email', 'phone1', 'active', 'getCategoriesStr', 'notes')
    list_filter = [BirthdayFilter,VolunteerActiveFilter, VolunteerCategoriesFilter]


class PatientAdmin(admin.ModelAdmin):
    fieldsets = [
       (_('Person'), {'fields': ['first_name', 'surname', 'birthdate']}),
       (_('Other'), {'fields': ['ward','diagnosis','notes']}),
    ]
    list_display = ('first_name', 'surname',
                    'birthdate', 'ward', 'diagnosis', 'notes')
    list_filter = [BirthdayFilter, PatientWardsFilter]

admin.site.register(Patient, PatientAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Duty, DutyAdmin)
admin.site.register(Category)
admin.site.register(Ward)
