"""dropship URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'worklogs', views.WorklogViewSet, basename='worklogs')
router.register(r'issues', views.IssueViewSet, basename='issues')
router.register(r'sprints', views.SprintViewSet, basename='sprints')
router.register(r'issue/(?P<pid>.+)/worklogs', views.IssueWorklogViewSet, basename='issue_worklog')
router.register(r'project/(?P<pid>.+)/sprints', views.ProjectSprintViewSet, basename='projects_sprint')
router.register(r'issue/(?P<iid>.+)/sprint', views.IssueSprintViewSet, basename='sprint_issue')
router.register(r'issue/(?P<pid>.+)/comments', views.IssueCommentViewSet, basename='comment_issue')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get_auth_token',views.get_auth_token,name='get_auth_token'),
    #path('drf/issue/get-post',views.IssueAPIView.as_view()),
    #path('drf/issue/get-put-delete/<int:id>',views.IssueDetails.as_view()),
    #path('drf/get-issue-title/<title>',views.IssueDetails.as_view()),
    path('drf/project/get-post',views.ProjectAPIView.as_view(),name="drf/projects"),
    path('drf/project/get-put-delete/<int:id>',views.ProjectDetails.as_view(),name="drf/project"),
    path('dprojects',views.returnProjects,name='projects'),
    path('dissues',views.returnIssues,name='issues'),
    path('issues_in_project/<int:id>',views.ProjectIssueAPI.as_view()),
    path('project/<int:p_id>/issue/<int:i_id>',views.ProjectIssueDetails.as_view()),
    path('dissue/<int:issue_id>',views.returnIssueIDOrUpdate,name='project_id'),
    #path('drf/assignee/<int:id>',views.IssueDetails.as_view()),
    #path('drf/label_delete/<int:id>',views.delete_label),
    path('', include(router.urls)),
]
