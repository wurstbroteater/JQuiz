import json

from django.core.management.base import BaseCommand

from quiz.models import Quiz


class Command(BaseCommand):
    help = 'Export quizzes with the given name to JSON'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the quiz to export')

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        try:
            quizzes = Quiz.objects.filter(name__icontains=name)
            if not quizzes.exists():
                self.stdout.write(self.style.ERROR(f"No quizzes found with name containing '{name}'"))
                return

            quiz_data = []
            for quiz in quizzes:
                questions = quiz.question_set.all()
                question_data = []
                for question in questions:
                    choices = question.choice_set.all()
                    choice_data = [{
                        choice.answer_symbol: choice.choice_text,
                        'is_correct': choice.is_correct,
                    } for choice in choices]

                    question_data.append({
                        'q_id': question.question_number,
                        'question': question.question,
                        'text_snippets': question.question_text,
                        'code_snippets': question.code_snippets,
                        'answers': choice_data,
                        'solution_text': question.solution,
                        # 'submit_date': question.submit_date.isoformat(),
                    })

                quiz_data.append({
                    'name': quiz.name,
                    'questions': question_data,
                })

            quizzes_json = json.dumps(quiz_data, indent=4)
            output_file = f'exported_{name}.json'

            with open(output_file, 'w') as f:
                f.write(quizzes_json)

            self.stdout.write(self.style.SUCCESS(f"Successfully exported quizzes to {output_file}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
