from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# -------------------------- Quiz --------------------------
class Quiz(models.Model):
    name = models.TextField(default='')

    def __str__(self):
        return self.name


class Question(models.Model):
    related_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_number = models.IntegerField()
    question = models.TextField()
    question_text = models.TextField(default='')
    code_snippets = models.TextField(default='')
    submit_date = models.DateField(default=timezone.now)
    solution = models.TextField(default='', blank=True)

    def __str__(self):
        return f"Question[{self.question}]"


class Choice(models.Model):
    answer_symbol = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.answer_symbol} : {self.choice_text}"


# -------------------------- Turn --------------------------
class QuizTurn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        state = "completed" if self.is_completed else "pending"
        return f"Turn {self.id} {state} {self.user.username} : {self.quiz}"


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turn = models.ForeignKey(QuizTurn, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.selected_choice if self.selected_choice else 'No answer'}"

    def __eq__(self, other):
        if not isinstance(other, UserAnswer):
            return False
        return (self.user == other.user and
                self.turn == other.turn and
                self.question == other.question and
                self.selected_choice == other.selected_choice)

    def __hash__(self):
        return hash((self.user, self.turn, self.question, self.selected_choice))


# -------------------------- Problem Report --------------------------
class ProblemReport(models.Model):
    title = models.TextField()
    problem_description = models.TextField()
    submit_date = models.DateField(default=timezone.now)
    submitted_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
