from django.shortcuts import render
from django.views.generic import View, FormView
from accounts.forms import SignUpForm, LoginForm
from django.shortcuts import redirect
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
# Create your views here.


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def form_valid(self, form, **kwargs):
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(self.request, user)
            return redirect(reverse("projects:projects_list"))
        else:
            form.add_error(None, "Invalid username or password.")
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return render(self.request, self.template_name, context)


class SignUpView(FormView):
    template_name = "accounts/sign_up.html"
    form_class = SignUpForm

    def form_valid(self, form):
        form.cleaned_data.pop("confirm_password", "None")
        user = User.objects.create(is_active=False, **form.cleaned_data)
        subject = "New user request for activation."
        message = "User with id={} request for activation.".format(user.id)
        mail_admins(subject, message)
        return redirect(reverse("login"))


def logout_view(request):
    logout(request)
    return redirect(reverse("login"))
