# Core Django imports.
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import (
    CreateView,
    ListView,
)

from django.http import HttpResponseRedirect
from django.shortcuts import render

# Blog application imports.
from blog.models.article_models import Article
from blog.models.comment_models import Comment
from blog.forms.blog.comment_forms import CommentForm

class CommentCreateView(CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = get_object_or_404(Article,
                                            slug=self.kwargs.get('slug'))
        comment.save()
        messages.success(self.request, "Comment Added successfully")
        return redirect('blog:article_comments', comment.article.slug)


class ArticleCommentList(ListView):
    context_object_name = "comments"
    paginate_by = 10
    template_name = "blog/comment/article_comments.html"

    def get_queryset(self):
        article = get_object_or_404(Article, slug=self.kwargs.get('slug'))
        queryset = Comment.objects.filter(article=article)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ArticleCommentList, self).get_context_data(**kwargs)
        context['article'] = get_object_or_404(Article,
                                               slug=self.kwargs.get('slug'))
        context['comment_form'] = CommentForm
        return context


# handling reply, reply view
class ReplyCreateView(CreateView):
    def reply_page(request):
        if request.method == "POST":

            form = CommentForm(request.POST)

            if form.is_valid():
                post_id = request.POST.get('article_id')  # from hidden input
                parent_id = request.POST.get('parent')  # from hidden input
                post_url = request.POST.get('article_url')  # from hidden input

                reply = form.save(commit=False)
    
                reply.post = Article(id=post_id)
                reply.parent = Comment(id=parent_id)
                reply.save()

                return redirect(article_url+'#'+str(reply.id))

        return redirect("/")