from django.shortcuts import render
from django.views.generic import View
from accounts.forms import SignUpForm

# Create your views here.

class LoginView(View):
    def get(self, request, **kwargs):
        return render(request, "accounts/login.html")

class SignUpView(View):
    def get(self, request, **kwargs):
        return render(request, "accounts/sign_up.html", {"form":SignUpForm})
