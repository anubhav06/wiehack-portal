from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Round, SubmissionForm, FormRequirements
from django.db import IntegrityError

# Create your views here.

@login_required(login_url="/login")
def index(request):

    round = Round.objects.filter(active=True).first()
    # If there is no active round, then find the next round which is going to be active.
    if round is None:
        next_round = Round.objects.filter(next_round=True).first()
        if next_round is None:
            total_rounds = Round.objects.all().count()

    def last_open_round():
        try:
            if next_round is not None:
                last_open_round = next_round.round_number - 1
            else:
                last_open_round = total_rounds
        except NameError:
            last_open_round = None
        return last_open_round
    
    return render(request, "portal/dashboard.html", {
        "round" : round,
        "last_open_round" : last_open_round()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "portal/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, "portal/login.html")  


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "portal/register.html", {
                "message": "Passwords must match."
            })

        # Input validation
        if not username or not email or not password or not confirmation:
            return render(request, "portal/register.html", {
                "message": "All fields required."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "portal/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "portal/register.html")


def submission(request):

    current_round = Round.objects.filter(active=True).first()
    form_requirements = FormRequirements.objects.filter(round=current_round).first()
    
    # If there is no active round, then find the next round which is going to be active.
    next_round = Round.objects.filter(next_round=True).first()
    if next_round is None:
        total_rounds = Round.objects.all().count()
        last_round = total_rounds
    else:
        last_round = Round.objects.get(round_number=next_round.round_number-1)

    if current_round is None:
        submission_form = SubmissionForm.objects.filter(team=request.user, round=last_round)
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
        "last_open_round" : last_round,
        "submission_form" : submission_form
    })