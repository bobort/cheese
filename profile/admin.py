from django.contrib import admin

from profile.models import Student, ExamScore


class StudentAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class ExamScoreAdmin(admin.ModelAdmin):
    search_fields = ('student__user__username', 'student__user__fist_name', 'student__user__last_name')


admin.site.register(Student, StudentAdmin)
admin.site.register(ExamScore, ExamScoreAdmin)
