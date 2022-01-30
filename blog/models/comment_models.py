# Core Django imports.
from django.db import models
from django.utils import timezone

# Blog application imports.
from blog.models.article_models import Article


class Comment(models.Model):

    name = models.CharField(max_length=250, null=False, blank=False)
    email = models.EmailField()
    comment = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                related_name='comments')

    parent=models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name='posts')
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return self.comment
    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)
