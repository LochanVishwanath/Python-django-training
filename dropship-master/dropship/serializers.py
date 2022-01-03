from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import Comment, Issue, Label, Project, Sprint, Worklog

class IssueSerializers(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class ProjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields='__all__'

class LabelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

class WorklogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worklog
        fields = '__all__'

class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'