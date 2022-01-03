from copy import Error
import json
from django.contrib import auth
from django.contrib.auth.models import Group
from django.core import paginator
from django.db.models.query import QuerySet
from django.http import HttpResponse,JsonResponse, request
from django.http.response import Http404
from rest_framework import viewsets,mixins
from django.contrib.auth import authenticate, get_permission_codename
import rest_framework
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework import permissions
from rest_framework import pagination
from rest_framework import serializers
from rest_framework.serializers import Serializer
from . models import Comment, Issue, Label, Project, Sprint, User, Worklog
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .serializers import CommentSerializer, IssueSerializers, ProjectSerializers, SprintSerializer, WorklogSerializer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import OR, SAFE_METHODS, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

class CustomProjectPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        #print("Standard" in request.user.groups.all())
        if request.user.groups.filter(name=["Admin"]).exists():
            return True
        return False
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        if obj.author == user:
            if user.groups.filter(name="Admin").exists():
                return True

class CustomSprintPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.groups.filter(name="Manager").exists() or request.user.groups.filter(name="Admin").exists():
            return True
        return False
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        elif obj.author == user:
            if user.groups.filter(name="Manager").exists() or request.user.groups.filter(name="Admin").exists():
                return True

class CustomIssuePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.groups.filter(name="Standard").exists() or request.user.groups.filter(name="Manager").exists() or request.user.groups.filter(name="Admin").exists():
            return True
        return False
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        elif obj.author == user:
            if user.groups.filter(name="Standard").exists() or user.groups.filter(name="Manager").exists() or user.groups.filter(name="Admin").exists():
                return True

@api_view(['POST'])
def get_auth_token(request):
    data = json.loads(request.body.decode("utf-8"))
    username = data.get('username')
    password = data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return HttpResponse("Username / Password not found",status=HTTP_404_NOT_FOUND)
    else:
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({
            "token": token.key
        })

class IssueViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    queryset = Issue.objects.all()
    serializer_class = IssueSerializers
    filter_backends = [DjangoFilterBackend]
    permission_classes=[IsAuthenticated & CustomIssuePermission]
    filterset_fields = ['id', 'title', 'type', 'description', 'project', 'label', 'status', 'reporter','watchers','assignee']

    def list(self, request, *args, **kwargs):
        if request.query_params.get('dsql') is not None:
            print(request.query_params['dsql'])
            issues = Issue.objects.raw('SELECT * FROM dropship_issue WHERE {}'.format(request.query_params['dsql']))
            #issues = Issue.objects.raw('SELECT * FROM dropship_issue WHERE type=\'BUG\'')
            serializers = IssueSerializers(issues,many=True)
            return Response(serializers.data)
        else:
            email = EmailMessage('Test', 'Test', to=['xoyimay411@rerunway.com'])
            email.send()
            return super().list(request, *args, **kwargs)

    def get_issue(self,id):
        try:
            return Issue.objects.get(id=id)
        except Issue.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
    
    def partial_update(self, request, *args, **kwargs):
        issue = self.get_issue(id=self.kwargs['pk'])
        if request.data.get('status') is not None:
            statuses = ["OPEN", "INPROGRESS", "INREVIEW", "QATESTING", "DONE"]
            if statuses.index(request.data['status']) - statuses.index(issue.status) == 1:
                return super(IssueViewSet, self).partial_update(request, *args, *kwargs)
        elif request.data.get('operation') == 'delete': 
            if request.data.get('label') is not None:
                label = Label.objects.get(label=request.data['label'])
                if label in issue.label.all():
                    issue.label.remove(label)
                    return Response("Label deleted",status=HTTP_202_ACCEPTED)
                else:
                    return Response('Label not present in issue',status=HTTP_404_NOT_FOUND)
            if request.data.get('watcher') is not None:
                user = User.objects.get(username=request.data['watcher'])
                if user in issue.watchers.all():
                    issue.watchers.remove(user)
                    return Response('Watcher removed',status=HTTP_202_ACCEPTED)
                else: 
                    return Response('Issue does not contain this user as its watcher',status=HTTP_404_NOT_FOUND)
        elif request.data.get('label'):
            label = Label.objects.get(label=request.data['label'])
            if label not in issue.label.all():
                issue.label.add(label)
                return Response("Label Added",status=HTTP_202_ACCEPTED)
            else: 
                return Response('Label not present',status=HTTP_404_NOT_FOUND)
        elif request.data.get('watcher') is not None:
            user = User.objects.get(username=request.data['watcher'])
            if user not in issue.watchers.all():
                issue.watchers.add(user)
                return Response('Watcher added',status=HTTP_202_ACCEPTED)
            else: 
                return Response('User doesnt exist',status=HTTP_404_NOT_FOUND)
        elif request.data.get('assignee'):
            user = User.objects.get(username = request.data['assignee'])
            issue.assignee = user
            return Response("Assigned Changed",status=HTTP_202_ACCEPTED)
        else:
            return super(IssueViewSet, self).partial_update(request, *args, *kwargs)

# class IssueAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes=[IsAuthenticated]
#     def get(self,request):
#         issues = Issue.objects.all()
#         serializer = IssueSerializers(issues,many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = IssueSerializers(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=HTTP_201_CREATED)
#         return Response(serializer.errors,HTTP_400_BAD_REQUEST)

# class IssueDetails(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes=[IsAuthenticated]
#     def get_issue(self,id):
#         try:
#             return Issue.objects.get(id=id)
#         except Issue.DoesNotExist:
#             return Response(status=HTTP_404_NOT_FOUND)
    
#     def get(self,request,id=None,title=None,description=None):
#         if title is not None:
#             try:
#                 issue = Issue.objects.filter(title=title)[0]
#                 serializer = IssueSerializers(issue)
#                 return Response(serializer.data)
#             except Issue.DoesNotExist:
#                 return Response(status=HTTP_404_NOT_FOUND)
#         if description is not None:
#             try:
#                 issue = Issue.objects.filter(description=description)[0]
#                 serializer = IssueSerializers(issue)
#                 return Response(serializer.data)
#             except Issue.DoesNotExist:
#                 return Response(status=HTTP_404_NOT_FOUND)

#         if id is not None:
#             issue = self.get_issue(id)
#             serializer = IssueSerializers(issue)
#             return Response(serializer.data)

#     def put(self,request,id):
#         issue = self.get_issue(id)
#         serializer = IssueSerializers(issue,data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors,HTTP_400_BAD_REQUEST)
    
#     def patch(self,request,id):
#         issue = self.get_issue(id)
#         new_issue = issue
#         if request.data.get('status') is not None:
#             statuses = ["OPEN", "INPROGRESS", "INREVIEW", "QATESTING", "DONE"]
#             if statuses.index(request.data['status']) - statuses.index(issue.status) == 1:
#                 new_issue.status = request.data['status']
            
#         if request.data.get('assignee') is not None:
#             try:
#                 user = User.objects.get(username = request.data['assignee'])
#                 new_issue.assignee = user
#             except User.DoesNotExist:
#                 return Response('Assignee does not exist',status=HTTP_404_NOT_FOUND)
        
#         if request.data.get('label') is not None:
#             if request.data.get('operation') == 'update':
#                 try:
#                     label = Label.objects.get(label = request.data['label'])
#                     new_issue.label = label
#                 except Label.DoesNotExist:
#                     return Response('Label does not exist',status=HTTP_404_NOT_FOUND)
#             elif request.data.get('operation') == 'delete':
#                 label = Label.objects.get(label=request.data['label'])
#                 issue = Issue.objects.get(id=id)
#                 if label in issue.label.all():
#                     issue.label.remove(label)
#                 else:
#                     return Response('Label not present in issue',status=HTTP_404_NOT_FOUND)
#                 return Response('Label Removed',status=HTTP_200_OK)


#         serializer = IssueSerializers(issue,data = IssueSerializers(new_issue).data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors,HTTP_400_BAD_REQUEST)
    
#     def delete(self,request,id):
#         issue = self.get_issue(id)
#         issue.delete()
#         return Response(status=HTTP_204_NO_CONTENT)


class ProjectAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[CustomProjectPermission & IsAuthenticated]

    def get(self,request):
        projects = Project.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(projects, request)
        serializer = ProjectSerializers(result_page,many=True)
        return Response(serializer.data)
        #return self.get_paginated_response(Serializer.data)
    
    def post(self, request):
        serializer = ProjectSerializers(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=HTTP_201_CREATED)
        return Response(serializer.errors,HTTP_400_BAD_REQUEST)

class ProjectDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[CustomProjectPermission]

    def get_project(self,id):
        try:
            project = Project.objects.get(id=id)
            if request.method in SAFE_METHODS or project.author.id == self.request.user.id:
                return project
            else:
                return None
        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
    
    def get(self,request,id):
        project = self.get_project(id)
        if project == None:
            return Response("You dont have permission to this project",status=HTTP_400_BAD_REQUEST)
        serializer = ProjectSerializers(project)
        return Response(serializer.data)

    def put(self,request,id):
        project = self.get_project(id)
        if project == None:
            return Response("You dont have permission to this project",status=HTTP_400_BAD_REQUEST)
        serializer = ProjectSerializers(project,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        project = self.get_project(id)
        if project == None:
            return Response("You dont have permission to this project",status=HTTP_400_BAD_REQUEST)
        project.delete()
        return Response(status=HTTP_204_NO_CONTENT)

class ProjectIssueAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[CustomIssuePermission]

    def get_project(self,id):
        try:
            return Project.objects.get(id=id)
        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

    def get(self,request,id):
        project = self.get_project(id)
        issues=project.issues.all()
        serializer = IssueSerializers(issues,many=True)
        return Response(serializer.data)

class ProjectIssueDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[CustomIssuePermission]

    def get_issue_from_project(self,p_id,i_id):
        try:
            project = Project.objects.get(id=p_id)
            return project.issues.all().get(id=i_id)
        except Project.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        except Issue.DoesNotExist:
            return Response('Issue with id {0} not in project with id {1}'.format(i_id,p_id),status=HTTP_404_NOT_FOUND)
    
    def get(self,request,p_id,i_id):
        try:
            issue = self.get_issue_from_project(p_id,i_id)
            serializer = IssueSerializers(issue)
            return Response(serializer.data)
        except AttributeError:
            return Response('Issue with id {0} not in project with id {1}'.format(i_id,p_id),status=HTTP_404_NOT_FOUND)

    def put(self,request,p_id,i_id):
        try:
            issue = self.get_issue_from_project(p_id,i_id)
            serializer = IssueSerializers(issue,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response('Issue with id {0} not in project with id {1}'.format(i_id,p_id),status=HTTP_404_NOT_FOUND)
    
    def delete(self,request,p_id,i_id):
        try:
            issue = self.get_issue_from_project(p_id,i_id)
            issue.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        except AttributeError:
            return Response('Issue with id {0} not in project with id {1}'.format(i_id,p_id),status=HTTP_404_NOT_FOUND)

class SprintViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    permission_classes=[CustomSprintPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title','start','end','status','project']
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer

    def partial_update(self, request, *args, **kwargs):
        current_status = self.get_object().status
        request_status = request.data['status']
        status = ["YET", "START", "STOP"]

        if status.index(request_status) - status.index(current_status) != 1:
            return Response('Sprint status can only move foward')
        else:
            super(SprintViewSet, self).partial_update(request, *args, *kwargs)

class ProjectSprintViewSet(viewsets.ModelViewSet):
    permission_classes=[CustomSprintPermission]
    serializer_class = SprintSerializer
    queryset = Sprint.objects.all()

    def create(self, request, *args, **kwargs):
        pid = int(self.kwargs['pid'])
        request.data["project"] = pid
        return super(ProjectSprintViewSet, self).create(request, *args, *kwargs)

class IssueSprintViewSet(viewsets.GenericViewSet,mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    permission_classes=[CustomSprintPermission]
    serializer_class = SprintSerializer
    queryset = Sprint.objects.all()

    def partial_update(self, request, *args, **kwargs):
        issue = Issue.objects.get(id=self.kwargs['iid'])
        sprint = Sprint.objects.get(id=self.kwargs['pk'])
        if issue.sprint is None:
            issue.sprint = sprint
            issue.save()
            return Response('Issue has been add to sprint',status=HTTP_200_OK)
        else:
            return Response('This issue is already a part of another sprint',status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        issue = Issue.objects.get(id=self.kwargs['iid'])
        sprint = Sprint.objects.get(id=self.kwargs['pk'])
        if issue.sprint is not None:
            issue.sprint = None
            issue.save()
            return Response('Issue has been removed from this sprint',status=HTTP_200_OK)
        else:
            return Response('This ticket is not part of this sprint',status=HTTP_400_BAD_REQUEST)   

class IssueCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        pid = int(self.kwargs['pid'])
        request.data['issue'] = pid
        return super(IssueCommentViewSet, self).create(request, *args, *kwargs)

class IssueWorklogViewSet(viewsets.ModelViewSet):
    serializer_class = WorklogSerializer
    queryset=Worklog.objects.all()

    def create(self, request, *args, **kwargs):
        issue_id = (self.kwargs['pid'])
        request.data['issue'] = issue_id
        return super(IssueWorklogViewSet, self).create(request, *args, *kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(IssueWorklogViewSet, self).destroy(request, *args, *kwargs)

class WorklogViewSet(viewsets.ModelViewSet):
    queryset = Worklog.objects.all()
    serializer_class = WorklogSerializer    

# @api_view(['DELETE'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def delete_label(request,id):
#     label = Label.objects.get(label=request.data['label'])
#     issue = Issue.objects.get(id=id)
#     if label in issue.label.all():
#         issue.label.remove(label)
#     else:
#         return Response('Label not present in issue',status=HTTP_404_NOT_FOUND)
#     return Response('Label Removed',status=HTTP_200_OK)

@csrf_exempt
def index(request):
    if request.method == 'POST':
        p = Project.objects.create(title=request.POST.get("a"))
        #p.save()
        return HttpResponse("hello world")

def returnProjects(request):
    p = Project.objects.all()
    
    return JsonResponse(list(p.values()),safe=False)

@csrf_exempt
def returnIssues(request):
    if request.method == 'GET':
        issues = Issue.objects.all()
        return JsonResponse(list(issues.values()),safe=False)
    elif request.method == 'POST':
        
        put = json.loads( request.body.decode('utf-8'))
        new_issue = Issue(title=put.get('title'),description=put.get('description'),type=put.get('type'),project = Project.objects.get(code = put.get('project')))
        
        new_issue.save()
        return JsonResponse(list(Issue.objects.all().values()),safe=False)

@csrf_exempt
def returnIssueIDOrUpdate(request,issue_id):
    issue = get_object_or_404(Issue,id=issue_id)
    if issue != Http404 and request.method == 'GET':
        data = {"issue":{"title":issue.title,"type":issue.type,"description":issue.description,"project":issue.project.code}}
        return JsonResponse(data)
    elif issue != Http404 and request.method == 'PUT':
        put = json.loads( request.body.decode('utf-8'))

        if put.get('title'):
            issue.title = put.get('title')
        if put.get('description'):
            issue.description = put.get('description')
        if put.get('type'):
            issue.type= put.get('type')
        if put.get('project'):
            project = Project.objects.get(code = put.get('project'))
            issue.project = project
        
        issue.save()
        data = {"issue":{"title":issue.title,"type":issue.type,"description":issue.description,"project":issue.project.code}}
        return JsonResponse(data,safe=False)
    elif issue != Http404 and request.method == 'DELETE':
        data = {"deleted_issue":{"title":issue.title,"type":issue.type,"description":issue.description,"project":issue.project.code}}
        issue.delete()
        return JsonResponse(data)
