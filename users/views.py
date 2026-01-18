from django.contrib import messages
from django.shortcuts import redirect, render

from users.forms import CustomUserCreationForm


def login_view(request):
    if request.method == "GET":
        return render(request, "pages/index.html")


def create_account(request):

    # Check if the request method is GET
    if request.method == "GET":

        # Initialize an empty form
        form = CustomUserCreationForm()

        # Render the form in the template
        return render(
            request,
            "pages/create-account.html",
            {"form": form}
        )

    # Check if the request method is POST
    elif request.method == "POST":

        # Populate the form with POST data
        form = CustomUserCreationForm(request.POST)

        # Validate the form data
        if form.is_valid():
            form.save()  # Save the user
            messages.success(  # Display a success message
                request,
                "Conta criada com sucesso! Faça login."
            )
            return redirect("/")

        # If the form is not valid, display an error message
        messages.error(
            request,
            "Corrija os erros abaixo."
        )

        # Re-render the form with error messages
        return render(
            request,
            "pages/create-account.html",
            {"form": form}
        )
