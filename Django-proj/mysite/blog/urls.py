from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/edit/',
        views.PostUpdateView.as_view(),
        name='post_edit'
    ),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
    path('search/', views.post_search, name='post_search'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('about/', views.about, name='about'),
]
