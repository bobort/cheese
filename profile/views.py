from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy

from profile.forms import StudentForm, UserForm
from profile.models import Student

from django.views.generic import CreateView


class CreateRegistration(CreateView):
    template_name = "form.html"
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('profile:create', kwargs={'user': self.object.pk})


class CreateProfile(CreateView):
    template_name = "form.html"
    model = Student
    form_class = StudentForm
    success_url = reverse_lazy('frontend:schedule')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = User.objects.get(pk=self.kwargs['user'])
        instance.save()
        return super().form_valid(form)
