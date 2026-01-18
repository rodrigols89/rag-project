from django.urls import resolve


def test_root_url_is_registered():
    """
    Testa se a rota / está registrada no sistema de rotas do Django.
    """

    # Arrange
    # (nenhuma preparação adicional é necessária)

    # Act
    match = resolve("/")

    # Assert
    assert match is not None
