from django.apps import apps


def test_users_app_is_installed():
    """
    Testa se o app 'users' está registrado em INSTALLED_APPS.
    """

    # Arrange
    # (nenhuma preparação extra é necessária)

    # Act
    app_config = apps.get_app_config("users")

    # Assert
    assert app_config.name == "users"
