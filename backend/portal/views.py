from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Round, SubmissionForm, FormRequirements, User, GradingSheet
from django.db import IntegrityError
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
import secrets
import string
from decouple import config


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
            elif user.groups.filter(name="Admin").exists():
                return HttpResponseRedirect(reverse("admin_index"))
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "portal/login.html", {
                "message": "Invalid username and/or password."
            })

    return render(request, "portal/login.html")  


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url="/login")
def index(request):

    if request.user.groups.filter(name="Judge").exists():
        return HttpResponseRedirect(reverse("judge_index"))

    current_round = Round.objects.filter(active=True).first()
    last_over_round = Round.objects.filter(round_over=True).order_by('-round_number').first()
    try:
        if current_round is None:
            user_eligible = last_over_round.eligible_teams.filter(username=request.user.username).first()
        else:
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

    if request.user.groups.filter(name="Judge").exists():
        return HttpResponseRedirect(reverse("judge_index"))

    current_round = Round.objects.filter(active=True).first()
    last_over_round = Round.objects.filter(round_over=True).order_by('-round_number').first()
    form_requirements = FormRequirements.objects.filter(round=current_round).first()
    try:
        if current_round is None:
            user_eligible = last_over_round.eligible_teams.filter(username=request.user.username).first()
        else:
            user_eligible = current_round.eligible_teams.filter(username=request.user.username).first()
    except AttributeError:
        user_eligible = None

    if current_round is None:
        submission_form = SubmissionForm.objects.filter(team=request.user, round=last_over_round)
    else:
        submission_form = SubmissionForm.objects.filter(team=request.user, round=current_round)

    if request.method == "POST":

        theme = request.POST.get("theme", False)
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
            elif file_ext.lower() not in ['.pdf']:
                return HttpResponse("Invalid file format", status=406)
        
        # Save the data
        try:
            submit_form = SubmissionForm.objects.create(theme=theme, github=github, youtube=youtube, file=file, team=request.user, round=current_round)
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
        submission_forms = SubmissionForm.objects.filter(round=current_round).all().order_by('id')
    else:
        submission_forms = SubmissionForm.objects.filter(round=last_over_round).all().order_by('id')

    grading_sheet = GradingSheet.objects.filter(user=request.user).first()

    return render(request, "portal/judge-dashboard.html", {
        "round" : current_round,
        "last_over_round" : last_over_round,
        "submission_forms" : submission_forms,
        "grading_sheet" :  grading_sheet
    })


@login_required(login_url="/login")
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def admin_index(request):

    if not request.user.groups.filter(name="Admin").exists():
        return HttpResponse("You are not authorised")

    if request.method == "POST":

        request_type = request.POST.get("request_type", "None")

        if request_type == "generate_credentials":
            print("Generating Credentials ... ")
            message = generate_credentials()
            return render(request, "portal/admin-dashboard.html", {
                "message" : message
            })
        
        elif request_type == "update_round2":
            print("Updating Round 2 access ... ")
            message = update_selected_teams(2)
            return render(request, "portal/admin-dashboard.html", {
                "message" : message
            })
        
        elif request_type == "update_round3":
            print("Updating Round 3 access ... ")
            message = update_selected_teams(3)
            return render(request, "portal/admin-dashboard.html", {
                "message" : message
            })
        
        else:
            print("Invalid Request")
            return render(request, "portal/admin-dashboard.html", {
                "message" : "Invalid Request"
            })
        
            

    return render(request, "portal/admin-dashboard.html")


# Helper functions
def generate_credentials():
    
    credentials = {
        "type": config('GOOGLE_AUTH_TYPE'),
        "project_id": config('GOOGLE_AUTH_PROJECT_ID'),
        "private_key_id": config('GOOGLE_AUTH_PRIVATE_KEY_ID'),
        "private_key": config('GOOGLE_AUTH_PRIVATE_KEY').replace('\\n', '\n').replace('\\\\', '\\'),
        "client_email": config('GOOGLE_AUTH_CLIENT_EMAIL'),
        "client_id": config('GOOGLE_AUTH_CLIENT_ID'),
        "auth_uri": config('GOOGLE_AUTH_AUTH_URI'),
        "token_uri": config('GOOGLE_AUTH_TOKEN_URI'),
        "auth_provider_x509_cert_url": config('GOOGLE_AUTH_AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": config('GOOGLE_AUTH_CLIENT_X509_CERT_URL'),
    }

    try:
        client = gspread.service_account_from_dict(credentials)

        sheet = client.open(config('SPREADSHEET_NAME')).sheet1
        portal_sheet = client.open(config('SPREADSHEET_PORTAL_NAME')).sheet1

        # Get all the values from the spreadsheet
        data = sheet.get_all_values()

        user_data = []
        user_data.append(['TeamID', 'Team Number' ,'TL Name', 'TL Email', 'Password'])

        teamID = data[1][0]

        for index, row in enumerate(data):
            # Pass the very first row as it is column headings
            if index == 0:
                continue

            if row[0] != teamID:
                teamID == row[0]

            if row[2] == "team leader":
                # Save the details
                alphabet = string.ascii_letters + string.digits + string.punctuation
                password = ''.join(secrets.choice(alphabet) for i in range(20))  # for a 20-character password

                try:
                    user = User.objects.create_user(username=row[4], email=row[4], password=password, first_name=row[3], teamID=row[0], team_number=row[22])
                    user.save()
                except Exception as e:
                    return "Error: " + str(e) + " while creating user"
                
                user_data.append([row[0], row[22], row[3], row[4], password])

        try:
            portal_sheet.update('A1', user_data)
        except:
            print("⚠️ Error while updating the spreadsheet")
            return "Error while updating the spreadsheet"

        print('Generated credentials ✅')
        return "Generated credentials successfully"

    except Exception as e:
        print("⚠️ An error occourred : " + str(e) + " with Google Sheets API")
        return "An error occurred with Google Sheets API: " + str(e) + ".Please try again later."
    

def update_selected_teams(round_number):

    credentials = {
        "type": config('GOOGLE_AUTH_TYPE'),
        "project_id": config('GOOGLE_AUTH_PROJECT_ID'),
        "private_key_id": config('GOOGLE_AUTH_PRIVATE_KEY_ID'),
        "private_key": config('GOOGLE_AUTH_PRIVATE_KEY').replace('\\n', '\n').replace('\\\\', '\\'),
        "client_email": config('GOOGLE_AUTH_CLIENT_EMAIL'),
        "client_id": config('GOOGLE_AUTH_CLIENT_ID'),
        "auth_uri": config('GOOGLE_AUTH_AUTH_URI'),
        "token_uri": config('GOOGLE_AUTH_TOKEN_URI'),
        "auth_provider_x509_cert_url": config('GOOGLE_AUTH_AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": config('GOOGLE_AUTH_CLIENT_X509_CERT_URL'),
    }
    
    try:
        client = gspread.service_account_from_dict(credentials)

        grading_sheet = client.open(config('SPREADSHEET_GRADING_SHEET_NAME')).get_worksheet(round_number-1)

        # Get all the values from the spreadsheet
        data = grading_sheet.get_all_values()

        for index, row in enumerate(data):
            # Pass the very first row as it is column headings
            if index == 0:
                continue

            if row[4].lower() == "selected":
                tl_email = row[3]
                try:
                    tl = User.objects.get(email=tl_email)
                except IntegrityError:
                    return "Team leader not found"
                
                round = Round.objects.get(round_number=round_number)
                round.eligible_teams.add(tl)
        
        print('Updated selected teams ✅')
        return "Updated selected teams successfully"

    except:
        print("⚠️ An error occourred ")
        return "An error occurred with Google Sheets API"
