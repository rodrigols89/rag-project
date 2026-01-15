from django.urls import resolve


def test_admin_url_is_registered():
    """
    Testa se a URL /admin/ está registrada no sistema de rotas do Django.
    """

    # Arrange
    # (não é necessário preparar nada além do carregamento do Django)

    # Act
    match = resolve('/admin/')

    # Assert
    assert match is not None
