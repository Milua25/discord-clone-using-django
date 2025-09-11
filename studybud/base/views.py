from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm


# room_numbers = [
#     {"id": 1, "name": "Room1"},
#     {"id": 2, "name": "Room2"},
#     {"id": 3, "name": "Room3"},
# ]


# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ""

    all_rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    all_topics = Topic.objects.all()
    room_count = all_rooms.count()
    context = {
        "rooms": all_rooms,
        "topics": all_topics,
        "room_count": room_count,
    }
    return render(request, 'base/home.html', context)


def rooms(request):
    all_rooms = Room.objects.all()
    context = {"rooms": all_rooms}
    return render(request, 'base/rooms.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('comment'),
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    context = {"form": form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    update_room = Room.objects.get(id=pk)
    form = RoomForm(request.POST or None, instance=update_room)

    if request.user != update_room.host:
        return HttpResponseForbidden()

    if form.is_valid():
        form.save()
        return redirect('home')
    context = {"form": form}
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    context = {"object": room}
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete_room.html', context)


def loginPage(request):
    page = "loginPage"
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        print(username, password)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username not found.')
            return redirect('login')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username/Password incorrect.')
                return redirect('login')

    context = {"page": page}
    return render(request, 'base/register_login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error occured during registration...')
            return redirect('register')
    context = {"form": form}
    return render(request, 'base/register_login.html', context)
