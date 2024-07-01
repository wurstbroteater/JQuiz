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
        fields = ['question', 'problem_description', 'submitted_by']
        widgets = {
            'question': forms.HiddenInput(),
            'submitted_by': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProblemReportForm, self).__init__(*args, **kwargs)
        self.fields['question'].widget.attrs['readonly'] = True
