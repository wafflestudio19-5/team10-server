from haystack import indexes
from set.models import Set


class SetIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, template_name='search/set_text.txt')
    set_id = indexes.IntegerField(model_attr='id')

    def get_model(self):
        return Set

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
