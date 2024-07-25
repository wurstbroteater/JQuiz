import json

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_date

from quiz.models import Choice, Question, Quiz


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
            for j_quiz in data:
                quiz = Quiz.objects.create(name=j_quiz['name'])
                for j_question in j_quiz['questions']:
                    question = Question.objects.create(
                        related_quiz=quiz,
                        question_number=int(j_question['q_id']),
                        question=str(j_question['question']),
                        question_text=str(j_question['text_snippets']),
                        code_snippets="\n".join(j_question['code_snippets']),
                        submit_date=parse_date(str(timezone.now().date())),
                        solution=str(j_question['solution_text'])
                    )

                    answer_symbol = "A"
                    for a in j_question['answers']:
                        Choice.objects.create(
                            answer_symbol=answer_symbol,
                            choice_text=a[answer_symbol],
                            is_correct=a['is_correct'],
                            question=question
                        )
                        answer_symbol = chr(ord(answer_symbol) + 1)

        self.stdout.write(self.style.SUCCESS('Quiz imported successfully'))
