from django.contrib import admin

from .models import Comment, Sprint, User, Project, Issue, Label, Worklog

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Label)
admin.site.register(Worklog)
admin.site.register(Comment)
admin.site.register(Sprint)
