from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter
import djoser

from .views import (
    SchoolView,
    CourseViewSet,
    RequestViewSet,
    TAViewSet,
    OfficeHourViewSet,
    UserViewSet,
    PasswordResetView,
)

v3_school_router = DefaultRouter()
v3_user_router = DefaultRouter()

v3_user_router.register(r'user', UserViewSet)
v3_school_router.register(r'courses', CourseViewSet)

course_router = NestedSimpleRouter(v3_school_router,
                                   r'courses',
                                   lookup='course')
course_router.register(r'requests', RequestViewSet)
course_router.register(r'tas', TAViewSet, base_name='ta')
course_router.register(r'officehours', OfficeHourViewSet)

password_reset_urls = [
    url(
        r'^reset/$',
        PasswordResetView.as_view(),
        name='password_reset'
    ),
    url(
        r'^reset/confirm/$',
        djoser.views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
]

urls = [
    url(r'^v3/', include(v3_user_router.urls, namespace='v3')),
    url(r'^v3/password/', include(password_reset_urls)),
    url(r'^v3/school/$', SchoolView.as_view()),
    url(r'^v3/school/', include(v3_school_router.urls, namespace='v3')),
    url(r'^v3/school/', include(course_router.urls, namespace='v3')),
]
