from django.urls import path

from users import views

urlpatterns = [
    path(
        route="",
        view=views.login_view,
        name="index"),
    path(
        route="create-account/",
        view=views.create_account,
        name="create-account"
    ),
]
