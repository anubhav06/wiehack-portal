from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    def __str__(self):
        return f"{self.username}"

# Round details
class Round(models.Model):

    round_number = models.IntegerField(default=1)
    round_description = models.CharField(max_length=500, default="round description here")
    download_template = models.CharField(max_length=500, default="https://www.bvpieee.in")
    active = models.BooleanField(default=False)
    # If this round is the next round, then True
    next_round = models.BooleanField(default=False)

    def __str__(self):
        return f"Round: {self.round_number} ---- Active: {self.active}"


# Submission Form 
class SubmissionForm(models.Model):

    github = models.CharField(max_length=100, blank=True)
    youtube = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='uploads', blank=True)
    team =  models.ForeignKey(User, related_name="team_submission", on_delete=models.CASCADE)
    round = models.ForeignKey(Round, related_name="round_submission", on_delete=models.CASCADE)

    def __str__(self):
        return f"Round: {self.round.round_number} ---- Team: {self.team.username}"


# Equal to the number of rounds. Set a new requirement for each round
class FormRequirements(models.Model):
    
    github = models.BooleanField(default=True)
    youtube = models.BooleanField(default=True)
    file = models.BooleanField(default=False)
    round = models.ForeignKey(Round, related_name="round_form", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.round.round_number}"