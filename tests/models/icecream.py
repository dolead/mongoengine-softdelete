from mongoengine import fields

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class IceCream(SoftDeleteNoCacheDocument):
    meta = {
        'collection': 'ice_cream',
        'soft_delete': {'deleted': True},
        'indexes': [ 'flavor' ],
        'strict': False
    }

    flavor = fields.StringField(required=True)
    color = fields.StringField(required=True)
    price = fields.FloatField(default=0)
    deleted = fields.BooleanField(default=False)
    created_at = fields.DateTimeField()
