from mongoengine import fields

from mongoengine_softdelete.document import SoftDeleteDocument, SoftDeleteNoCacheDocument


class Nestor(SoftDeleteNoCacheDocument):
    meta = {
        'collection': 'nested',
        'soft_delete': {'dikt': {'hide_me': 'yes'}},
        # 'soft_delete': {'dikt__hide_me__contains': 'yes'},
        'strict': False
    }

    dikt = fields.DictField()