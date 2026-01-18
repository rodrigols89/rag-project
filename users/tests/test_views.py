from django.test import Client, SimpleTestCase

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


class TestRootView(SimpleTestCase):

    def test_root_view_renders_correct_template(self):
        """
        Testa se a view da rota / renderiza o template correto.
        """

        # Arrange
        client = Client()

        # Act
        response = client.get("/")

        # Assert
        self.assertTemplateUsed(response, "pages/index.html")
