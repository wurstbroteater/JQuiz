from django import forms

from .models import Choice, ProblemReport


class ChoiceForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        if question:
            self.fields['choices'].queryset = question.choice_set.all()


class ProblemReportForm(forms.ModelForm):
    class Meta:
        model = ProblemReport
        fields = ['title', 'problem_description', 'submitted_by']
        widgets = {
            'submitted_by': forms.HiddenInput(),
            'title': forms.Textarea(attrs={'rows': 1})
        }
