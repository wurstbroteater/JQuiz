import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_date
from quiz.models import Choice, Question, Quiz
from pathlib import Path


class Command(BaseCommand):
    help = 'Import a quiz from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The file path to the JSON file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        self.stdout.write("Start importing quiz")
        with open(file_path, 'r') as file:
            data = json.load(file)
            # use file name as quiz name
            quiz = Quiz.objects.create(name=Path(file_path).stem)
            for q in data:
                question = Question.objects.create(
                    related_quiz=quiz,
                    question_number=int(q['q_id']),
                    question=str(q['question']),
                    question_text=str(q['text_snippets']),
                    code_snippets="\n".join(q['code_snippets']),
                    submit_date=parse_date(str(timezone.now().date())),
                    solution=str(q['solution_text'])
                )

                answer_symbol = "A"
                for a in q['answers']:

                    Choice.objects.create(
                        answer_symbol=answer_symbol,
                        choice_text=a[answer_symbol],
                        is_correct=a['is_correct'],
                        question=question
                    )
                    answer_symbol = chr(ord(answer_symbol) + 1)

        self.stdout.write(self.style.SUCCESS('Quiz imported successfully'))
