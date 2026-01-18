from django.test import Client

OK_STATUS_CODE = 200


def test_root_get_returns_200():
    """
    Testa se um GET / retorna status HTTP 200.
    """

    # Arrange
    client = Client()

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == OK_STATUS_CODE
