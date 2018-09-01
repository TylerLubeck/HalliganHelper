from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from .views import TuftsRegistrationView

urlpatterns = patterns(
    'tas.views',
    url(r'^accounts/register/$',
        TuftsRegistrationView.as_view(),
        name='register'),
    url(r'^accounts/',
        include('registration.backends.default.urls')),
    url(r'^taSystem$',
        RedirectView.as_view(url=reverse_lazy('ModularHomePage')),
        name='taSystem'),
    url(r'^login_or_register',
        RedirectView.as_view(url=reverse_lazy('ModularHomePage')),
        name='login_or_register'),
    url(r'^ta/updatephoto',
        'update_photo',
        name='update_photo'),
)
