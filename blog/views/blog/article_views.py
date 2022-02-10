# Standard Python Library imports.
from functools import reduce
import operator

# Core Django imports.
from django.contrib import messages
from django.db.models import Q
from django.views.generic import (
    DetailView,
    ListView,
)

# Blog application imports.
from blog.models.article_models import Article
from blog.models.category_models import Category
from blog.forms.blog.comment_forms import CommentForm
from django.shortcuts import get_object_or_404, render, redirect

class ArticleListView(ListView):
    context_object_name = "articles"
    paginate_by = 12
    queryset = Article.objects.filter(status=Article.PUBLISHED, deleted=False)
    template_name = "blog/article/home.html"
    articles = context_object_name

    def get_context_data(self, *args, **kwargs):

        articles = Article.objects.all()

        # enumerate_articles = enumerate(articles)

        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(approved=True)

        global categories
        
        categories = Category.objects.filter(approved=True)

        

        recent_articles = Article.objects.filter(
            status=Article.PUBLISHED, deleted=False).order_by("-date_published")[:5]

        latest = Article.objects.filter(
            status=Article.PUBLISHED, deleted=False).order_by("-date_published")[0]

        
        articles_list = Article.objects.filter(status=Article.PUBLISHED, deleted=False)

        trending_article_list = Article.objects.filter(status=Article.PUBLISHED, deleted=False).order_by('views')

        most_trending_article = trending_article_list[len(trending_article_list)-1]
        other_trending_articles = trending_article_list[0:len(trending_article_list)-2]

        number_of_articles = len(articles)
        category_range = range(len(categories))

        # context['tag_articles_list'] = tag_articles_list
        context['recent_articles'] = recent_articles
        context['latest'] = latest
        context['most_trending_article'] =  most_trending_article
        # context['enumerate_articles'] =  enumerate_articles
        context['other_trending_articles'] =  other_trending_articles
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article/article_detail.html'

    def get_context_data(self, **kwargs):
        session_key = f"viewed_article {self.object.slug}"
        if not self.request.session.get(session_key, False):
            self.object.views += 1
            self.object.save()
            self.request.session[session_key] = True

        kwargs['related_articles'] = \
            Article.objects.filter(category=self.object.category, status=Article.PUBLISHED).order_by('?')[:3]

        kwargs['article'] = self.object
        kwargs['comment_form'] = CommentForm()
        kwargs['categories'] = Category.objects.filter(approved=True)
        return super().get_context_data(**kwargs)


class ArticleSearchListView(ListView):
    model = Article
    paginate_by = 12
    context_object_name = 'search_results'
    template_name = "blog/article/article_search_list.html"

    def get_queryset(self):
        """
        Search for a user input in the search bar.

        It pass in the query value to the search view using the 'q' parameter.
        Then in the view, It searches the 'title', 'slug', 'body' and fields.

        To make the search a little smarter, say someone searches for
        'container docker ansible' and It want to search the records where all
        3 words appear in the article content in any order, It split the query
        into separate words and chain them.
        """

        query = self.request.GET.get('q')

        if query:
            query_list = query.split()
            search_results = Article.objects.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(slug__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(body__icontains=q) for q in query_list))
            )

            if not search_results:
                messages.info(self.request, f"No results for '{query}'")
                return search_results.filter(status=Article.PUBLISHED, deleted=False)
            else:
                messages.success(self.request, f"Results for '{query}'")
                return search_results.filter(status=Article.PUBLISHED, deleted=False)
        else:
            messages.error(self.request, f"Sorry you did not enter any keyword")
            return []

    def get_context_data(self, **kwargs):
        """
            Add categories to context data
        """
        context = super(ArticleSearchListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(approved=True)
        return context


class TagArticlesListView(ListView):
    """
        List articles related to a tag.
    """
    model = Article
    paginate_by = 12
    context_object_name = 'tag_articles_list'
    template_name = 'blog/article/tag_articles_list.html'

    def get_queryset(self):
        """
            Filter Articles by tag_name
        """
        global tag_name
        tag_name = self.kwargs.get('tag_name', '')
        
        global tag_articles_list

        if tag_name:
            tag_articles_list = Article.objects.filter(tags__name__in=[tag_name],
                                                       status=Article.PUBLISHED,
                                                       deleted=False
                                                       )

            if not tag_articles_list:
                messages.info(self.request, f"No '{tag_name}' Articles")
                return tag_articles_list
            else:
                messages.success(self.request, f"'{tag_name}' Articles")
                return tag_articles_list
        else:
            messages.error(self.request, "Invalid tag")
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(approved=True)
        context['tag_articles_list'] = tag_articles_list
        return context
