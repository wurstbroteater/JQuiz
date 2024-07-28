# JQuiz v0.2

JQuiz is a web platform where users can answer multiple-choice questions related to Java in an encouraging manner.

## Requirements

- Python 3.10.12 or later

## Installation

You might want to consider using `venv`.

```shell
pip install -r /path/to/requirements.txt
python manage.py makemigrations quiz && python manage.py migrate
python manage.py createsuperuser
python manage.py import_quiz /path/to/quiz.json 
```

## JSON Format

The format of the JSON file (`quiz.json`) is still in development. Therefore, the following sample might not be up-to-date.

```json
[
  {
    "name": "Chapter 0",
    "questions": [
      {
        "q_id": 1,
        "question": "1. The answer to what?",
        "text_snippets": "arthur.properties\r\nguide=Ford",
        "code_snippets": [
          "42:  final \u2423\u2423\u2423 x = dT.negate();",
          "System.out.println(\"Don't Panic\");"
        ],
        "answers": [
          {
            "is_correct": true,
            "A": " Answer<Life>"
          },
          {
            "is_correct": false,
            "B": " The Universe!"
          },
          {
            "is_correct": true,
            "C": " Answer<Everything>"
          },
          {
            "is_correct": false,
            "D": " Comparator<Integer>"
          }
        ],
        "solution_text": "A, C. A is correct because 42 and C is correct because 42."
      }
    ]
  }
]
```

## Examples

### Quiz Exporting

The following snippets shows how to export the quiz Chapter0 from database to JSON.

``` shell
 python manage.py export_quiz "Chapter 0"
```
