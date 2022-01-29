from haystack import indexes
from user.models import User


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, template_name='search/user_text.txt')
    user_id = indexes.IntegerField(model_attr='id')
    city = indexes.CharField(model_attr='city')
    country = indexes.CharField(model_attr='country')

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
