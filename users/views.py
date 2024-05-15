from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import profileSearch, paginateProfiles
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
import logging
from django.db.models import Q


# Create your views here.
def loginUser(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("profiles")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "user does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("profiles")
        else:
            messages.error(request, "Password is incorrect")

    return render(request, "users/login_register.html")


def logoutUSer(request):
    logout(request)
    messages.info(request, "user logged out")
    return redirect("login")


# from django.contrib import messages


logger = logging.getLogger(__name__)


def registerUser(request):
    page = "register"
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        # Username is already handled in the form clean method
        try:
            user.save()
        except Exception as e:
            logger.error(f"Error during user save: {e}")
            messages.error(request, "An unexpected error occurred! Please try again.")
            return render(
                request, "users/login_register.html", {"page": page, "form": form}
            )

        # Check if a UserProfile already exists and if not, create one
        try:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                messages.success(request, "User account was created!")
                login(request, user)
                return redirect("profiles")
            else:
                messages.error(request, "User account already has a profile.")
        except Exception as e:
            logger.error(f"Error during profile creation: {e}")
            messages.error(request, "An unexpected error occurred! Please try again.")
            return render(
                request, "users/login_register.html", {"page": page, "form": form}
            )
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")

    context = {"page": page, "form": form}
    return render(request, "users/login_register.html", context)

    """
    Renders the profiles page with a list of all profiles.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A rendered HTML response containing the profiles page with the list of profiles.
    """


def profiles(request):
    profiles, search_query = profileSearch(request)
    custom_range, profiles = paginateProfiles(request, profiles, 3)
    context = {
        "profiles": profiles,
        "search_query": search_query,
        "custom_range": custom_range,
    }
    return render(request, "users/profiles.html", context)


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    print(profile)
    topSkills = profile.skill_set.exclude(description__exact="")

    otherSkills = profile.skill_set.filter(description="")
    context = {"profile": profile, "topSkills": topSkills, "otherSkills": otherSkills}
    return render(request, "users/user-profile.html", context)


@login_required(login_url="login")
def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    projects = profile.projects_set.all()
    context = {"profile": profile, "skills": skills, "projects": projects}
    return render(request, "users/account.html", context)


@login_required(login_url="login")
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("account")

    context = {"form": form}
    return render(request, "users/profile_form.html", context)


@login_required(login_url="login")
def createSkill(request):
    form = SkillForm()
    rofile = request.user.profile
    if request.method == "POST":
        form = SkillForm(request.POST)
        profile = request.user.profile
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, "Skill was added successfully")
            return redirect("account")

    context = {"form": form}
    return render(request, "users/skills_form.html", context)


@login_required(login_url="login")
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    form = SkillForm(instance=skill)

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)

        if form.is_valid():
            form.save()
            messages.success(request, "Skill was updated successfully")
            return redirect("account")

    context = {"form": form}
    return render(request, "users/skills_form.html", context)


@login_required(login_url="login")
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill was deleted successfully")
        return redirect("account")
    context = {"object": skill}
    return render(request, "delete_template.html", context)

@login_required(login_url="login")
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context= { 
        'messageRequests':messageRequests,
        'unreadCount':unreadCount,
    } 
    return render(request, 'users/inbox.html', context)

@login_required(login_url="login")
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {
        'message':message,
    }
    return render(request, 'users/message.html', context)
def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    try:
        sender = request.user.profile
    except:
        sender = None
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            messages.success(request, "Your message was successfully sent")
            return redirect("user-profile", pk=recipient.id)
    context = {
        'recipient':recipient,
        'form':form,
    }
    return render(request, 'users/message-form.html', context)