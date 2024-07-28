from django.contrib import admin

from .models import Quiz, Question, Choice, UserAnswer, QuizTurn, ProblemReport


class QuizTurnAdmin(admin.ModelAdmin):
    model = QuizTurn


class UserAnswerAdmin(admin.ModelAdmin):
    model = UserAnswer


class QuizAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fieldsets = [
        (None, {"fields": ["name"]}),
    ]


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ["question", "choice_text", "is_correct"]
    fieldsets = [
        (None, {"fields": ["answer_symbol", "choice_text", "is_correct"]}),
    ]


class ChoiceInline(admin.StackedInline):
    model = Choice


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "submit_date"]
    fieldsets = [
        (None, {"fields": ["question", "question_text", "code_snippets"]}),
        ("Solution", {"fields": ["solution"]}),
        ("Related Quiz", {"fields": ["related_quiz"]}),
        ("Date information", {"fields": ["submit_date"]}),
    ]
    inlines = [ChoiceInline]


class ProblemReportAdmin(admin.ModelAdmin):
    model = ProblemReport


admin.site.register(ProblemReport, ProblemReportAdmin)
admin.site.register(QuizTurn, QuizTurnAdmin)
admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
