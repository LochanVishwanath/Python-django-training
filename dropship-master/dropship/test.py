import json

from django.contrib.auth import get_user_model

User = get_user_model()
from django.http import response
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from dropship.models import Issue
from dropship.serializers import IssueSerializers


class ProjectTestCase(APITestCase):

    project_url = reverse("drf/projects")
    data={"title":"title1","description":"desc1","code":"code1"}

    def setUp(self):
        self.user = User.objects.create(username="lochan",password="abc123")
        self.token = Token.objects.create(user = self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token "+self.token.key)

    def test_project_post_valid(self):
        response = self.client.post(self.project_url,self.data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
    
    def test_project_post_invalid(self):
        response = self.client.post(self.project_url, {"description":"desc1","code":"code1"})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

    def test_project_get(self):
        response = self.client.get(self.project_url)
        print(response.json())
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_project_get_by_id(self):
        self.client.post("/drf/project/get-post",self.data)
        response = self.client.get("/drf/project/get-put-delete/1")
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_project_put(self):
        response = self.client.post("/drf/project/get-post",self.data)
        self.assertEqual(response.data["description"],"desc1")
        response = self.client.put("/drf/project/get-put-delete/1",{"title":"title1","description":"desc1 updated","code":"code1"})
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data["description"],"desc1 updated")

    def test_project_delete(self):
        response = self.client.post("/drf/project/get-post",self.data)
        self.assertEqual(response.data["description"],"desc1")
        response = self.client.delete("/drf/project/get-put-delete/1")
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)

