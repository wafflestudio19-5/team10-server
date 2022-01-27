from haystack import indexes
from user.models import User


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    q = indexes.EdgeNgramField(document=True, use_template=True, template_name='search/track_text.txt')
    id = indexes.IntegerField(model_attr='id')

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
