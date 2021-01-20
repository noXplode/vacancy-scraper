from django import forms

CHOICES = [('1', 'Удаленно по Украине'), ('2', 'Удаленно другие страны'), ('3', 'Харьков не удаленно')]


class SearchForm(forms.Form):
    search_string = forms.CharField(label='', max_length=100)
    q_choice = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_string'].widget.attrs.update({'class': 'form-control',
                                                          'type': 'text',
                                                          'placeholder': 'Search',
                                                          'aria-label': 'Search'})
        self.fields['q_choice'].widget.attrs.update({'class': 'form-check-input'})
