from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from profile.forms import StudentCreationForm, StudentChangeForm
from profile.models import Student, ExamScore, Payment, Appointment


class StudentAdmin(UserAdmin):
    model = Student
    add_form = StudentCreationForm
    form = StudentChangeForm
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email', 'last_name', 'first_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Student info'), {'fields': ('graduation_year', 'degree', 'exam', 'test_date')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


admin.site.register(Student, StudentAdmin)


class StudentSearchAdmin(admin.ModelAdmin):
    search_fields = ('student__email', 'student__first_name', 'student__last_name')


admin.site.register(ExamScore, StudentSearchAdmin)
admin.site.register(Payment, StudentSearchAdmin)
admin.site.register(Appointment, StudentSearchAdmin)
