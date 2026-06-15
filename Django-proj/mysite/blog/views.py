from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from taggit.models import Tag
from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[tag])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = None
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_object(self, queryset=None):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        slug = self.kwargs.get('slug')
        
        # Create date range to handle timezone conversions
        # The URL uses the local date, so we need to find posts
        # published on that date in the local timezone
        from datetime import date
        target_date = date(year, month, day)
        start_of_day = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        )
        end_of_day = start_of_day + timedelta(days=1)
        
        return get_object_or_404(
            self.get_queryset().filter(
                publish__gte=start_of_day,
                publish__lt=end_of_day,
                slug=slug
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['comment_form'] = CommentForm()
        context['comment_count'] = self.object.comment_count
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = self.object
            if request.user.is_authenticated:
                new_comment.name = request.user.username
                new_comment.email = request.user.email
            new_comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect(self.object.get_absolute_url())
        context = self.get_context_data()
        context['comment_form'] = comment_form
        return self.render_to_response(context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        # Handle tags - use clear() and add() for proper taggit handling
        tags_list = form.cleaned_data.get('tags', [])
        self.object.tags.clear()
        if tags_list:
            self.object.tags.add(*tags_list)  # add() works with string tag names
        messages.success(self.request, 'Post created successfully!')
        return response


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def get_object(self, queryset=None):
        from datetime import date
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        slug = self.kwargs.get('slug')
        
        # Create date range to handle timezone conversions
        target_date = date(year, month, day)
        start_of_day = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        )
        end_of_day = start_of_day + timedelta(days=1)
        
        return get_object_or_404(
            Post.objects.filter(
                publish__gte=start_of_day,
                publish__lt=end_of_day,
                slug=slug
            )
        )

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        response = super().form_valid(form)
        # Handle tags - use clear() and add() for proper taggit handling
        tags_list = form.cleaned_data.get('tags', [])
        self.object.tags.clear()
        if tags_list:
            self.object.tags.add(*tags_list)  # add() works with string tag names
        messages.success(self.request, 'Post updated successfully!')
        return response


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def get_object(self, queryset=None):
        from datetime import date
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        slug = self.kwargs.get('slug')
        
        # Create date range to handle timezone conversions
        target_date = date(year, month, day)
        start_of_day = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time())
        )
        end_of_day = start_of_day + timedelta(days=1)
        
        return get_object_or_404(
            Post.objects.filter(
                publish__gte=start_of_day,
                publish__lt=end_of_day,
                slug=slug
            )
        )

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


def post_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query),
            status='published'
        )
    return render(request, 'blog/post_search.html', {
        'query': query,
        'results': results
    })


def about(request):
    return render(request, 'blog/about.html')
