from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import Count
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import UserAnswer, Quiz, Question, Choice, QuizTurn, ProblemReport
from django.contrib.auth.decorators import login_required
from .forms import ChoiceForm, ProblemReportForm
from django.core.exceptions import PermissionDenied
from django.db.models import Max

from quiz.models import Question


class IndexView(generic.ListView):
    template_name = "quiz/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-submit_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "quiz/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "quiz/results.html"


# --------------------------------------- Leaderboard ----------------------------------

def leaderboard_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaderboard = (UserAnswer.objects
                   .filter(question__related_quiz=quiz, selected_choice__is_correct=True)
                   .values('user__username')
                   .annotate(total_correct=Count('id'))
                   .order_by('-total_correct'))

    return render(request, 'quiz/leaderboard.html', {
        'quiz': quiz,
        'leaderboard': leaderboard,
    })


# --------------------------------------- Quiz ----------------------------------

def quiz_overview(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz/quiz_overview.html', {'quizzes': quizzes})


@login_required
def quiz_start(request, quiz_id):
    user = request.user
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = quiz.question_set.first()
    turn = QuizTurn.objects.create(user=user, quiz=quiz)
    return redirect('question', turn_id=turn.id, question_id=question.id)


@login_required
def question_view(request, turn_id, question_id):
    turn = get_object_or_404(QuizTurn, id=turn_id)
    if request.user != turn.user:
        raise PermissionDenied
    question = get_object_or_404(Question, id=question_id)
    choices = question.choice_set.all()

    if request.method == 'POST':
        form = ChoiceForm(request.POST, question=question)
        if form.is_valid():
            selected_choices = form.cleaned_data['choices']
            for selected_choice in selected_choices:
                UserAnswer.objects.update_or_create(
                    user=turn.user,
                    turn=turn,
                    question=question,
                    defaults={
                        'selected_choice': selected_choice
                    }
                )
            next_question = turn.quiz.question_set.filter(id__gt=question.id).first()
            if next_question:
                return redirect('question', turn_id=turn.id, question_id=next_question.id)
            else:
                turn.is_completed = True
                turn.save()
                return redirect('results', turn_id=turn.id)
    else:
        form = ChoiceForm(question=question)

    previous_question = turn.quiz.question_set.filter(id__lt=question.id).last()
    next_question = turn.quiz.question_set.filter(id__gt=question.id).first()

    return render(request, 'quiz/question.html', {
        'quiz': turn,
        'question': question,
        'choices': choices,
        'form': form,
        'previous_question': previous_question,
        'next_question': next_question,
    })


def results_view(request, turn_id):
    turn = get_object_or_404(QuizTurn, id=turn_id)
    user = request.user
    quiz = turn.quiz
    questions = quiz.question_set.all()
    results = []

    for question in questions:
        user_answers = UserAnswer.objects.filter(user=user, question=question, turn=turn).all()
        solutions = Choice.objects.filter(question=question, is_correct=True).all()
        correct_ones = []
        for answer in user_answers:
            if answer.selected_choice.is_correct:
                correct_ones.append(answer.selected_choice)
        results.append({
            'question': question,
            'user_answer': ", ".join(list(
                map(lambda a: f"'{a.selected_choice.answer_symbol}. {a.selected_choice.choice_text}'", user_answers))),
            'correct': len(correct_ones) == len(solutions),
            'solution': question.solution,
        })

    return render(request, 'quiz/results.html', {
        'quiz': quiz,
        'results': results,
    })


# --------------------------------------- Problem Reporting ---------------------------------------

def report_problem(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = ProblemReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('problem_reported')  # Redirect to a success page or the same form
    else:
        form = ProblemReportForm(initial={'question': question})

    return render(request, 'quiz/report_problem.html', {'form': form, 'question': question})


def problem_reported(request):
    return render(request, 'quiz/problem_reported.html')
