from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UpdateEmailForm, DeleteAccountForm
from quiz.models import QuizTurn
from quiz.views import get_user_progress


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def profile(request):
    user = request.user
    turns = list(map(lambda t: (t.quiz.name, get_user_progress(t.user, t.quiz)),
                     QuizTurn.objects.filter(user=user, is_completed=True).order_by('quiz_id')))
    temp_grouped_turns = {}

    for quiz, info in turns:
        if quiz not in temp_grouped_turns:
            temp_grouped_turns[quiz] = []
        temp_grouped_turns[quiz].append(info)

    # Remove duplicates by converting lists of dictionaries to sets of frozensets and back to lists of dictionaries
    for quiz in temp_grouped_turns:
        unique_dicts = {frozenset(d.items()) for d in temp_grouped_turns[quiz]}
        temp_grouped_turns[quiz] = [dict(d) for d in unique_dicts]

    grouped_turn = [{'quiz': q, 'data': i} for q, i in temp_grouped_turns.items()]

    pending_turns = QuizTurn.objects.filter(user=user, is_completed=False).count()
    return render(request, 'user/profile.html',
                  {'data': grouped_turn, 'pending_turns': pending_turns})


@login_required
def update_email(request):
    if request.method == 'POST':
        form = UpdateEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email was successfully updated!')
            return redirect('profile')
    else:
        form = UpdateEmailForm(instance=request.user)
    return render(request, 'user/update_email.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')
    else:
        form = DeleteAccountForm()
    return render(request, 'user/delete_account.html', {'form': form})


@login_required
@csrf_exempt
def delete_incomplete_turns(request):
    if request.method == 'POST':
        user = request.user
        QuizTurn.objects.filter(user=user, is_completed=False).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)
