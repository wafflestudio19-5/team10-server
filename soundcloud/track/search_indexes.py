from haystack import indexes
from track.models import Track


class TrackIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True, template_name='search/track_text.txt')
    track_id = indexes.IntegerField(model_attr='id')
    genre_name = indexes.CharField(model_attr='genre__name')
    artist = indexes.CharField(model_attr='artist')
    pub_date = indexes.DateTimeField(model_attr='created_at')

    def get_model(self):
        return Track

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
