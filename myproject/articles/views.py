from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from django.core.paginator import Paginator
from .models import Article, Tag, SavedArticle, Comment
from .forms import CommentForm

# Create your views here.
def index(request):
    articles = Article.objects.filter(is_public=True).order_by('-pub_date')

    #Пагинация

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj  = paginator.get_page(page_number)

    return render (request, 'articles/index.html', {'page_obj': page_obj})

def article_list(request):
    articles = Article.objects.filter(is_public=True)

    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'author':
        articles = articles.order_by('author__username')
    elif sort_by == 'title':
        articles = articles.order_by('title')
    elif sort_by == 'tags':
        articles = articles.order_by('tags__name')
    else:
        articles = articles.order_by('-pub_date')  

    
    query = request.GET.get('q')

    if query:
        articles = articles.filter(Q(title__icontains = query) | Q(content__icontains = query))
    
    #Пагинация

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj  = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
        'query':query,
        'current_sort':sort_by
    }

    return render (request, 'articles/articles_list.html', context)


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = Comment.objects.filter(article=article)

    if request.method == "POST":
        if not request.user.is_authenticate:
            return redirect('login')
        
        form = CommentForm (request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            article.user = request.user

            comment.save()
            return redirect('article_detail', pk=pk)
        
    else:
        form = CommentForm()

    context = {
        'article':article,
        'comments': comments,
        'form': form
    }

    return render (request, 'articles/article_detail.html', context)

@login_required
def save_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    SavedArticle.objects.get_or_create(user = request.user, aricle = article)

    return redirect('article_detail', pk=pk)

@login_required
def unsave_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    SavedArticle.objects.filter(user=request.user, article=article).delete()

    return redirect('article_detail', pk=pk)

@login_required
def saved_articles(request):
    saved_articles = SavedArticle.objects.filter(user=request.user).select_related('article')
    return render(request, 'articles/saved_articles.html', {'saved_articles': saved_articles})

def custom_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()

    return render(request, 'registarion/login.html', {'form': form})


