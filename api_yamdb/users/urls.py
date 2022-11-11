from django.urls import include, path

from rest_framework.routers import DefaultRouter

from users.views import APIGetToken, APISignup, UsersViewSet


router = DefaultRouter()

router.register(r'users', UsersViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignup.as_view()),
    path('v1/auth/token/', APIGetToken.as_view()),
]
