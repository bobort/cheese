from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from profile.forms import StudentCreationForm, StudentChangeForm
from profile.models import Student, ExamScore, Order, Appointment, Product, OrderLineItem, Staff, AgendaItem, Course, \
    Testimonial


class StudentAdmin(UserAdmin):
    model = Student
    add_form = StudentCreationForm
    form = StudentChangeForm
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-last_login',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Student info'), {'fields': ('graduation_year', 'degree', 'exam', 'test_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('last_login', 'email', 'first_name', 'last_name', 'exam', 'is_staff')


admin.site.register(Student, StudentAdmin)


class StudentSearchAdmin(admin.ModelAdmin):
    search_fields = ('student__email', 'student__first_name', 'student__last_name')


admin.site.register(ExamScore, StudentSearchAdmin)
admin.site.register(Appointment, StudentSearchAdmin)


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    raw_id_fields = ('product', )


class OrderAdmin(StudentSearchAdmin):
    inlines = [OrderLineItemInline, ]


admin.site.register(Order, OrderAdmin)


class OrderLineItemAdmin(admin.ModelAdmin):
    search_fields = ('product__name', 'order__student__first_name', 'order__student__last_name')


admin.site.register(OrderLineItem, OrderLineItemAdmin)


class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('owners', )
    search_fields = ('name', 'notes')


admin.site.register(Product, ProductAdmin)


admin.site.register(Course)
admin.site.register(AgendaItem)
admin.site.register(Staff)
admin.site.register(Testimonial)
