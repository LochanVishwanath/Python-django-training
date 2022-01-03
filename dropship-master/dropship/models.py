from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    # If there are any fields needed add here.

    def __str__(self):
        return self.username

class Project(TimestampModel):
    title = models.CharField(max_length=128)
    description = models.TextField()
    code = models.CharField(max_length=64, unique=True, null=False)
    author =  models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return "{0} {1}".format(self.code, self.title)

class Label(TimestampModel):
    label = models.CharField(max_length=128, null=False)

    def __str__(self):
        return "{0}".format(self.label)

class Sprint(TimestampModel):
    START = "START"
    STOP = "STOP"
    YET = "YET"
    STATUS = [(YET, YET), (START, START), (STOP, STOP)]
    title = models.CharField(max_length=20)
    start = models.DateField(default=timezone.now())
    end = models.DateField(default=timezone.now())
    status = models.CharField(max_length=15, choices=STATUS, default=YET, null=False)
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.CASCADE, related_name="sprints"
    )
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    def __str__(self):
        return self.title

class Issue(TimestampModel):
    BUG = "BUG"
    TASK = "TASK"
    STORY = "STORY"
    EPIC = "EPIC"
    TYPES = [(BUG, BUG), (TASK, TASK), (STORY, STORY), (EPIC, EPIC)]

    OPEN = "OPEN"
    INPROGRESS = "INPROGRESS"
    INREVIEW = "INREVIEW"
    CODECOMPLETE = "CODECOMPLETE"
    QATESTING = "QATESTING"
    DONE = "DONE"
    STATUSES = [(OPEN, OPEN), (INPROGRESS, INPROGRESS), (INREVIEW, INREVIEW), (QATESTING, QATESTING), (DONE, DONE)]

    title = models.CharField(max_length=128)
    description = models.TextField()

    type = models.CharField(max_length=8, choices=TYPES, default=BUG, null=False)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues", null=False
    )

    status = models.CharField(max_length=15, choices=STATUSES, default=OPEN, null=False)
    label = models.ManyToManyField(Label,blank=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.DO_NOTHING, null=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="reported_issues", null=True, blank=True)
    watchers = models.ManyToManyField(User,blank=True)
    assignee = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="assigned_issues", null=True, blank=True)


    def __str__(self):
        return "{0}-{1}".format(self.project.code, self.title)

class Worklog(TimestampModel):
    time = models.IntegerField(default=60)

    issue = models.ForeignKey(Issue, on_delete=models.DO_NOTHING, null=False, blank=False, related_name='worklog')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False, blank=False)

    def __str__(self):
        return "{0} {1} {2}".format(self.time,self.issue,self.user)

class Comment(TimestampModel):
    description = models.CharField(max_length=200)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "{0}".format(self.description)

@receiver(pre_save,sender = Issue)
def send_email_when_issue_updated(sender,instance,*args,**kwargs):
    if instance.id is not None:
        previous = Issue.objects.get(id=instance.id)
        #send_email(instance)
        if previous.title != instance.title:
            print("Issue title changed form {0} to {1}".format(previous.title,instance.title))
        if previous.description != instance.description:
            print("Issue description changed form {0} to {1}".format(previous.description,instance.description))
        print("Email sent")

@receiver(pre_save,sender = Comment)
def send_email_when_comment_added_or_updated(sender,instance,*args,**kwargs):
    if instance.id is None:
        print("New comment added to {} Issue".format(instance.issue))
        #send_email(instance.issue)
    else:
        print("Comment in issue {} is updated".format(instance.issue))
        #send_email(instance.issue)