from django import forms
from .models import Post, Comment


class TagsInput(forms.TextInput):
    """Custom widget to properly display tag names as comma-separated string"""
    def value_from_datadict(self, data, files, name):
        return super().value_from_datadict(data, files, name)
    
    def format_value(self, value):
        # If value is a QuerySet of Tag objects, convert to comma-separated names
        if hasattr(value, 'all'):  # It's a QuerySet or Manager
            return ', '.join(tag.name for tag in value.all())
        # If it's already a string or list, return as-is
        if isinstance(value, list):
            return ', '.join(str(v) for v in value)
        return value or ''


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'body', 'status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'post-url-slug'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': TagsInput(attrs={
                'class': 'form-control',
                'placeholder': 'django, python, webdev'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if isinstance(tags_str, str):
            # Split by comma and clean up whitespace
            return [t.strip() for t in tags_str.split(',') if t.strip()]
        return tags_str


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment...'
            }),
        }
