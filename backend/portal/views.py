from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Round, SubmissionForm, FormRequirements
from django.db import IntegrityError
import os

# Create your views here.

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if user.groups.filter(name="Judge").exists():
                return HttpResponseRedirect(reverse("judge_index"))
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "portal/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, "portal/login.html")  


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# def register(request):
#     if request.method == "POST":
#         username = request.POST["username"]
#         email = request.POST["email"]

#         # Ensure password matches confirmation
#         password = request.POST["password"]
#         confirmation = request.POST["confirmation"]
#         if password != confirmation:
#             return render(request, "portal/register.html", {
#                 "message": "Passwords must match."
#             })

#         # Input validation
#         if not username or not email or not password or not confirmation:
#             return render(request, "portal/register.html", {
#                 "message": "All fields required."
#             })

#         # Attempt to create new user
#         try:
#             user = User.objects.create_user(username, email, password)
#             user.save()
#         except IntegrityError:
#             return render(request, "portal/register.html", {
#                 "message": "Username already taken."
#             })
#         login(request, user)
#         return HttpResponseRedirect(reverse("index"))
    
#     return render(request, "portal/register.html")


@login_required(login_url="/login")
def index(request):

    current_round = Round.objects.filter(active=True).first()
    last_over_round = Round.objects.filter(round_over=True).order_by('-round_number').first()
    try:
        user_eligible = current_round.eligible_teams.filter(username=request.user.username).first()
    except AttributeError:
        user_eligible = None

    return render(request, "portal/dashboard.html", {
        "round" : current_round,
        "last_over_round" : last_over_round,
        "user_eligible" : user_eligible
    })


@login_required(login_url="/login")
def submission(request):

    current_round = Round.objects.filter(active=True).first()
    last_over_round = Round.objects.filter(round_over=True).order_by('-round_number').first()
    form_requirements = FormRequirements.objects.filter(round=current_round).first()
    try:
        user_eligible = current_round.eligible_teams.filter(username=request.user.username).first()
    except AttributeError:
        user_eligible = None

    if current_round is None:
        submission_form = SubmissionForm.objects.filter(team=request.user, round=last_over_round)
    else:
        submission_form = SubmissionForm.objects.filter(team=request.user, round=current_round)

    if request.method == "POST":

        username = request.POST.get("teamID", False)
        github = request.POST.get("github", False)
        youtube = request.POST.get("youtube", False)
        file = request.FILES.get("input_file", False)

        # Input Validation
        if form_requirements.github and (not github):
            return render(request, "portal/submission.html", {
                "message" : "GitHub missing",
                "form" : form_requirements,
                "round" : current_round
            })
        if form_requirements.youtube and (not youtube):
            return render(request, "portal/submission.html", {
                "message" : "YouTube missing",
                "form" : form_requirements,
                "round" : current_round
            })
        if form_requirements.file and (not file):
            return render(request, "portal/submission.html", {
                "message" : "File missing",
                "form" : form_requirements,
                "round" : current_round
            })
        # Optional Validation- Checks if the user tries to "hack", by changing the input field's teamID, which is disabled by default.
        if username != request.user.username:
            return HttpResponse("WARNING! Don't try to do this again. You'll be disqualified.")
        
        # Check if user has already submitted the form
        if submission_form:
            return HttpResponse("We have already receieved your response.\nNeed help? Reach us on discord for immediate help. ")

        # Check if user is selected for this round
        if not user_eligible:
            return HttpResponse("You are not eligible for this Round")

        # Input file validation
        if file:
            file_ext = os.path.splitext(file.name)[1]
            if file.size > 5242880:
                return HttpResponse("File size should be less than 5MB", status=406)
            elif file_ext.lower() not in ['.pptx']:
                return HttpResponse("Invalid file format", status=406)
        
        # Save the data
        try:
            submit_form = SubmissionForm.objects.create(github=github, youtube=youtube, file=file, team=request.user, round=current_round)
            submit_form.save()
        except IntegrityError:
            return render(request, "portal/submission.html", {
                "message" : "Error. Please contact the organizers.",
                "form" : form_requirements,
                "round" : current_round
            })

        return HttpResponseRedirect(reverse("submission"))

    # GET Method ----

    return render(request, "portal/submission.html", {
        "form" : form_requirements,
        "round" : current_round,
        "last_open_round" : last_over_round,
        "submission_form" : submission_form,
        "user_eligible" : user_eligible
    })


@login_required(login_url="/login")
@user_passes_test(lambda u: u.groups.filter(name='Judge').exists())
def judge_index(request):

    if not request.user.groups.filter(name="Judge").exists():
        return HttpResponse("You are not authorised")

    current_round = Round.objects.filter(active=True).first()
    last_over_round = Round.objects.filter(round_over=True).order_by('-round_number').first()
    if current_round:
        submission_forms = SubmissionForm.objects.filter(round=current_round).all()
    else:
        submission_forms = SubmissionForm.objects.filter(round=last_over_round).all()

    return render(request, "portal/judge-dashboard.html", {
        "round" : current_round,
        "last_over_round" : last_over_round,
        "submission_forms" : submission_forms,
    })