from rest_framework.exceptions import APIException, ValidationError
from rest_framework import permissions, status
from django.conf import settings
from guardian.shortcuts import assign_perm
import boto3, os, re

def get_presigned_url(url, method, full_url=True):
    if url is None:
        return None

    if method not in [ 'get_object', 'put_object' ]:
        raise ValueError("method choices: ('get_object', 'put_object')")

    if full_url:
        key = url.replace(settings.S3_BASE_URL, '')

    presigned_url = boto3.client(
        's3',
        region_name=settings.S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    ).generate_presigned_url(
        ClientMethod=method,
        Params={
            'Bucket': settings.S3_BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=300
    )

    return presigned_url

def assign_object_perms(user, instance):
    """
    Assigns permission to modify and delete the instance to the user.
    """
    kwargs = {
        'app_label': instance._meta.app_label,
        'model_name': instance._meta.model_name
    }

    assign_perm('%(app_label)s.change_%(model_name)s' % kwargs, user, instance)
    assign_perm('%(app_label)s.delete_%(model_name)s' % kwargs, user, instance)


class CustomObjectPermissions(permissions.IsAuthenticatedOrReadOnly, permissions.DjangoObjectPermissions):
    pass


class ConflictError(APIException):
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('Already existing name.')
    default_code = 'conflict'


class MediaUploadMixin:
    """
    Must be used with 'rest_framework.serializers.ModelSerializer'.
    """

    media_types = ('audio', 'image')
    content_types = ('track', 'set', 'user_profile', 'user_header')
    media_paths = {
        'audio' : {
            'track':        settings.S3_BASE_URL + settings.S3_MUSIC_TRACK_DIR,
        },
        'image' : {
            'track':        settings.S3_BASE_URL + settings.S3_IMAGES_TRACK_DIR,
            'set':          settings.S3_BASE_URL + settings.S3_IMAGES_SET_DIR,
            'user_profile': settings.S3_BASE_URL + settings.S3_IMAGES_USER_PROFILE_DIR,
            'user_header':  settings.S3_BASE_URL + settings.S3_IMAGES_USER_HEADER_DIR,
        },
    }
    extensions = {
        'audio': ('.wav', '.flac', '.aiff', '.alac', 'mp3', '.aac', '.ogg', '.oga', '.mp4', '.mp2', '.m4a', '.3gp', '.3g2', '.mj2', '.amr', '.wma'),
        'image': ('.jpg', '.png'),
    }
    filename_pattern = re.compile('^[a-zA-Z0-9\/\!\-\_\.\*\'\(\)]+$')

    def get_audio_presigned_url(self, instance):
        if self.context['request'].data.get('audio_filename') is None:
            return None

        return get_presigned_url(instance.audio, 'put_object')

    def get_image_presigned_url(self, instance):
        if self.context['request'].data.get('image_filename') is None:
            return None

        return get_presigned_url(instance.image, 'put_object')

    def get_unique_url(self, filename, media_type, content_type, model=None):
        if filename is None:
            return None

        try:
            url = MediaUploadMixin.media_paths[media_type][content_type] + filename
        except KeyError:
            raise ValueError(f"media_type choices: {MediaUploadMixin.media_types}, content_type choices: {MediaUploadMixin.content_types}")

        model = model or self.Meta.model
        name, ext = os.path.splitext(url)
        queryset = model.objects.exclude(id=getattr(self.instance, 'id', None))

        while queryset.filter(**{media_type: url}).exists():
            if re.search(r'\-\d+$', name):
                num = re.search(r'\d+$', name).group(0)
                name = re.sub(r'\d+$', str(int(num)+1), name)
            else:
                name += '-1'
            url = name + ext
        
        return url

    def validate_audio_filename(self, value):
        if not self.check_extension(value, 'audio'):
            raise ValidationError("Unsupported audio file extension.")

        if not self.check_filename(value):
            raise ValidationError("Incorrect audio filename format.")

        return value

    def validate_image_filename(self, value):
        if not self.check_extension(value, 'image'):
            raise ValidationError("Unsupported image file extension.")

        if not self.check_filename(value):
            raise ValidationError("Incorrect image filename format.")

        return value

    @staticmethod
    def check_extension(filename, media_type):
        try:
            valid_extensions = MediaUploadMixin.extensions[media_type]
        except KeyError:
            raise ValueError(f"media_type choices: {MediaUploadMixin.media_types}")

        return filename.lower().endswith(valid_extensions)

    @staticmethod
    def check_filename(filename):

        return re.search(MediaUploadMixin.filename_pattern, filename)
