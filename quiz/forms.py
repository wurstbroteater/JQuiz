from django import forms

from .models import Choice, ProblemReport


class ChoiceForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        selected_choices = kwargs.pop('pre_selection', None)
        question = kwargs.pop('question')

        super(ChoiceForm, self).__init__(*args, **kwargs)

        self.fields['choices'].queryset = question.choice_set.all()
        if selected_choices:
            self.fields['choices'].initial = list(map(lambda c: c.id, selected_choices))


class ProblemReportForm(forms.ModelForm):
    class Meta:
        model = ProblemReport
        fields = ['title', 'problem_description', 'submitted_by']
        widgets = {
            'submitted_by': forms.HiddenInput(),
            'title': forms.Textarea(attrs={'rows': 1})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProblemReportForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['submitted_by'].initial = user
        else:
            self.fields['submitted_by'].required = False
