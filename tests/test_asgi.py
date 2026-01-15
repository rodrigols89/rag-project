from core.asgi import application


def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """

    # Arrange
    # (nenhuma preparação manual é necessária)

    # Act
    app = application

    # Assert
    assert callable(app)
