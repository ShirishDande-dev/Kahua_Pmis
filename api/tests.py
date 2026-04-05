import pytest
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.response import Response
from typing import cast
from pmis.tests import user, data_user, project


class TestAuthenticationViewSet:
    @pytest.mark.django_db
    def test_login(self, user):
        client = APIClient()
        response = cast(Response, client.post('/api/token/', {'username': user.username, 'password': 'password123'}))
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data # type: ignore
        assert 'refresh' in response.data # type: ignore

    @pytest.mark.django_db
    def test_refresh(self, user):

        client = APIClient()
        client.force_authenticate(user=user)
        # Obtain a valid token pair first
        login_response = cast(Response, client.post('/api/token/', {'username': user.username, 'password': 'password123'}))
        assert login_response.status_code == status.HTTP_200_OK
        assert login_response.data is not None
        refresh_token = login_response.data['refresh']

        refresh_response = cast(Response, client.post('/api/token/refresh/', {'refresh': refresh_token}))
        assert refresh_response.status_code == status.HTTP_200_OK
        assert refresh_response.data is not None
        assert 'access' in refresh_response.data
        assert 'refresh' not in refresh_response.data
