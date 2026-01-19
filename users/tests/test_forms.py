import pytest
from django.contrib.auth.models import User

from users.forms import CustomUserCreationForm


@pytest.mark.django_db
def test_custom_user_creation_form_creates_user():
    """
    Testa se um formulário válido cria um usuário no banco de dados.
    """

    # ---------------- ( Arrange ) ----------------
    form_data = {
        "username": "usuario_teste",
        "email": "usuario_teste@email.com",
        "password1": "SenhaForte123!",
        "password2": "SenhaForte123!",
    }
    form = CustomUserCreationForm(data=form_data)

    # ------------------ ( Act ) ------------------
    is_valid = form.is_valid()

    if is_valid:
        form.save()

    # ----------------- ( Assert ) ----------------
    assert User.objects.filter(
        username="usuario_teste"
    ).exists()
