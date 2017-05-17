from djangocms_text_ckeditor.widgets import TextEditorWidget
from hvad.forms import TranslatableModelForm

from .models import Entry


class EntryForm(TranslatableModelForm):
    class Meta:
        model = Entry

    widget = TextEditorWidget
        
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = EntryForm.widget()
