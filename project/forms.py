from django.forms import ModelForm, widgets
from django import forms
from .models import Projects


class ProjectForm(ModelForm):
    class Meta:
        model = Projects
        # fields = "__all__"
        fields = [
            "title",
            "featured_image",
            "description",
            "demo_link",
            "source_link",
            "tags",
        ]
        widgets = {
            "tags": forms.CheckboxSelectMultiple(),
        }

        def __init__(self, *args, **kwargs):
            super(CLASS_NAME, self).__init__(*args, **kwargs)

            for name, field in self.fields.items():
                field.widget.attrs.update({ 'class': 'input'})
            # self.fields["title"].widget.attrs.update(
            #     {
            #         "class": "input",
            #     }
            # )
