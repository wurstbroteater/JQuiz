from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views import generic

from quiz.models import Question
from .forms import ChoiceForm, ProblemReportForm
from .models import UserAnswer, Quiz, Choice, QuizTurn


class IndexView(generic.ListView):
    template_name = "index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.order_by("-submit_date")[:5]


class DetailView(generic.DetailView):
    """
    Shows all details of a single Question
    """
    model = Question
    template_name = "quiz/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        total_questions = Question.objects.filter(related_quiz=question.related_quiz).count()
        context['total_questions'] = total_questions
        return context


# --------------------------------------- Leaderboard ----------------------------------

def leaderboard_overall_view(request):
    quizzes = Quiz.objects.all()
    return render(request, 'leaderboard/leaderboard.html',
                  {'leaderboard_data': list(map(lambda q: _get_leaderboard(q), quizzes))})


def leaderboard_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'leaderboard/leaderboard_quiz.html', {
        'user_progress': get_user_progress(request.user, quiz),
        'leaderboard_data': _get_leaderboard(quiz),
    })


def _get_leaderboard(quiz):
    turns = QuizTurn.objects.filter(quiz=quiz, is_completed=True)
    user_scores = list(map(lambda turn: _get_user_score(turn), turns))
    key_avg_score = 'average_score'
    user_scores = sorted(user_scores, key=_get_user_score_rank)

    distinct_scores = {}
    for d in user_scores:
        username = d['username']
        if username not in distinct_scores:
            distinct_scores[username] = d

    return {
        'quiz': quiz,
        'user_scores': list(distinct_scores.values()),
        'average_quiz_score': round(
            sum(d[key_avg_score] for d in user_scores) / len(user_scores) if user_scores else 0,
            2),
    }


def _get_user_score_rank(user_score):
    """
    - Primary: best_score
    - Secondary: average_score
    - Tertiary: correct_turns
    """
    rank = (-user_score['best_score'], -user_score['average_score'], -user_score['correct_turns'])
    return rank


def _get_user_score(turn):
    return get_user_progress(turn.user, turn.quiz) | {
        "username": turn.user.username
    }


def _foo(turn):
    correct_user_answers = UserAnswer.objects.filter(turn=turn, selected_choice__is_correct=True).values(
        'question').distinct().count()
    total_questions = Question.objects.filter(related_quiz=turn.quiz).count()
    return correct_user_answers * 100.0 / total_questions


def get_user_progress(user, quiz):
    turns = QuizTurn.objects.filter(user=user, quiz=quiz, is_completed=True)
    scores = [_foo(turn) for turn in turns]
    best_score = max(scores, default=0)
    average_score = sum(scores) / len(scores) if scores else 0
    return {
        'correct_turns': len([turn for turn in turns if turn.is_correct()]),
        'completed_turns': len(turns),
        'best_score': round(best_score, 2),
        'average_score': round(average_score, 2),
    }


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
    already_selected_user_answers = list(UserAnswer.objects.filter(
        user=turn.user,
        turn=turn,
        question=question).all())
    already_selected_choices = list(map(lambda ua: ua.selected_choice, already_selected_user_answers))
    if request.method == 'POST':
        form = ChoiceForm(request.POST, question=question, pre_selection=already_selected_choices)
        if form.is_valid():
            selected_choices = form.cleaned_data['choices']
            # Handle add or update
            for selected_choice in selected_choices:
                answer, _ = UserAnswer.objects.update_or_create(
                    user=turn.user,
                    turn=turn,
                    question=question,
                    selected_choice=selected_choice
                )
                if selected_choice in already_selected_choices:
                    already_selected_user_answers.remove(answer)

            # Handle remove
            for answer in already_selected_user_answers:
                answer.delete()

            next_question = turn.quiz.question_set.filter(id__gt=question.id).first()
            if next_question:
                return redirect('question', turn_id=turn.id, question_id=next_question.id)
            else:
                turn.is_completed = True
                turn.save()
                return redirect('results', turn_id=turn.id)
    else:
        form = ChoiceForm(question=question, pre_selection=already_selected_choices)

    previous_question = turn.quiz.question_set.filter(id__lt=question.id).last()
    next_question = turn.quiz.question_set.filter(id__gt=question.id).first()
    choices = question.choice_set.all()

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
        results.append({
            'question': question,
            'user_answer': ", ".join(list(
                map(lambda a: f"'{a.selected_choice.answer_symbol}. {a.selected_choice.choice_text}'", user_answers))),
            'correct': len(user_answers.filter(selected_choice__is_correct=True)) == len(solutions),
            'solution': question.solution,
        })

    return render(request, 'quiz/results.html', {
        'quiz': quiz,
        'results': results,
    })


# --------------------------------------- Problem Reporting ---------------------------------------

def report_problem(request):
    if request.method == 'POST':
        form = ProblemReportForm(request.POST, user=request.user if request.user.is_authenticated else None)
        previous_page = request.POST.get('referer_url', request.META.get('HTTP_REFERER', '/'))
        if form.is_valid():
            problem_report = form.save(commit=False)
            if request.user.is_authenticated:
                problem_report.submitted_by = request.user
            else:
                problem_report.submitted_by = None
            problem_report.save()
            return redirect(previous_page)
    else:
        form = ProblemReportForm()

    return render(request, 'report_problem.html', {'form': form})
