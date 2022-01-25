from typing_extensions import Required
from mongoengine import fields, Document

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class Album(SoftDeleteNoCacheDocument):
    meta = {
        'collection': 'album',
        'indexes': [ 'name', 'author' ],
        'strict': False,
        'soft_delete': {'deleted': True},
    }

    name = fields.StringField(required=True)
    author = fields.StringField(required=True)
    created_at = fields.DateTimeField()
    deleted = fields.BooleanField(default=False)

    @property
    def photos(self):
        return Photo.objects(album=self)


class Photo(SoftDeleteNoCacheDocument):
    meta = {
        'collection': 'photo',
        'indexes': [ 'filepath', 'author', 'created_at' ],
        'strict': False,
        'soft_delete': {'deleted': True},
    }

    filepath = fields.StringField(Required=True)
    author = fields.StringField(required=True)
    created_at = fields.DateTimeField()
    exif = fields.DictField()
    deleted = fields.BooleanField(default=False)
    album = fields.ReferenceField(Album)
