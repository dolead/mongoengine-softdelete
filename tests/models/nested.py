from mongoengine import fields

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class Nested(SoftDeleteNoCacheDocument):
    meta = {
        'collection': 'nested',
        'soft_delete': {'dikt__hide_me__contains': 'yes'},
        'strict': False
    }

    dikt = fields.DictField()
