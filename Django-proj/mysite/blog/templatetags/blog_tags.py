from django import template
from django.db.models import Count
from taggit.models import Tag
from ..models import Post

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.objects.filter(status='published').count()


@register.inclusion_tag('blog/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.objects.filter(
        status='published'
    ).order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.inclusion_tag('blog/tag_cloud.html')
def show_tag_cloud():
    tags = Tag.objects.all()
    return {'tags': tags}
