from django.contrib import admin

from .models import UserQuestion, Answer, Question


class AnswerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Question)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserQuestion)

