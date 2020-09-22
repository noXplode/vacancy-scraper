from django import forms


class SearchForm(forms.Form):
    search_string = forms.CharField(label='', max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_string'].widget.attrs.update({'class': 'form-control', 'type': 'text', 'placeholder': 'Search', 'aria-label': 'Search'})
