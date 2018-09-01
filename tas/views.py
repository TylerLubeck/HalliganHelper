import logging

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from registration.backends.default.views import RegistrationView
from registration.signals import user_registered, user_activated

from .utils import check_ta
from .custom_user_forms import EmailUserCreationForm, EmailAuthenticationForm


logger = logging.getLogger(__name__)


def user_confirmed(sender, user, request, **kwargs):
    check_ta(user)
    logger.info('Confirmed user: user_id=%s', user.pk)

user_activated.connect(user_confirmed)


class TuftsRegistrationView(RegistrationView):
    form_class = EmailUserCreationForm


def login_or_register(request):
    if request.method == 'POST':
        register_form = EmailUserCreationForm(request.POST)
        login_form = EmailAuthenticationForm(request.POST)
    else:
        register_form = EmailUserCreationForm()
        login_form = EmailAuthenticationForm()
    template_vars = {
        'register': register_form,
        'login': login_form
    }
    return render(request,
                  'tas/login_or_register.html',
                  template_vars)


# Necessary so that the csrf token can be loaded for the ajax calls on the page.
@ensure_csrf_cookie
def ModularHomePage(request):
    return render(request, 'logged_in.html', {})
