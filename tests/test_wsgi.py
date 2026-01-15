from core.wsgi import application


def test_wsgi_application_is_created():
    """
    Testa se a aplicação WSGI do Django é criada corretamente.
    """

    # Arrange
    # (nenhuma preparação manual é necessária)

    # Act
    app = application

    # Assert
    assert callable(app)
