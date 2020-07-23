from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request, 'todo/home.html')


def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signup_user.html', {'form': UserCreationForm(), 'error': 'Username already exists.'})
        else:
            return render(request, 'todo/signup_user.html', {'form': UserCreationForm(),'error': 'Passwords didn\'t match.'})


def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/login_user.html', {'form': AuthenticationForm()})
    else:
        user_exists = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user_exists:
            login(request, user_exists)
            return redirect('current_todos')
        else:
            return render(request, 'todo/login_user.html', {'form': AuthenticationForm(), 'error': 'User credentials invalid.'})


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def current_todos(request):
    todos = Todo.objects.filter(user=request.user, completed_on__isnull=True).order_by('created_on')
    todo_count = todos.count()
    return render(request, 'todo/current_todos.html', {'todos': todos, 'todo_count': todo_count})


@login_required
def create(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form': TodoForm})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html', {'form': TodoForm, 'error': 'Bad data entered.'})


@login_required
def view_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = TodoForm(instance=todo)
    return render(request, 'todo/view_todo.html', {'todo': todo, 'form': form})


@login_required
def edit_todo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/edit_todo.html', {'todo': todo, 'form': form})
    else:
        form = TodoForm(request.POST, instance=todo)
        try:
            form.save()
            return redirect('view_todo', todo_pk)
        except ValueError:
            return render(request, 'todo/edit_todo.html', {'form': form, 'error': 'Bad data entered.'})


@login_required
def complete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.completed_on = timezone.now()
        todo.save()
        return redirect('current_todos')


@login_required
def delete_todo(request, todo_pk):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
        todo.completed_on = timezone.now()
        todo.delete()
        return redirect('current_todos')


@login_required
def completed_todos(request):
    todos = Todo.objects.filter(user=request.user, completed_on__isnull=False).order_by('-completed_on')
    todo_count = todos.count()
    return render(request, 'todo/completed.html', {'todos': todos, 'todo_count': todo_count})
