from tests.base import TestCase

from mongoengine import fields

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class NestedModel(SoftDeleteNoCacheDocument):
    meta = {'collection': 'nested', 'strict': False,
            'soft_delete': {'dikt': {'hide_me': 'yes'}},
    }

    dikt = fields.DictField()


class TestNestedSubKeyQueries(TestCase):
    def setUp(self):
        NestedModel.drop_collection()

    def tearDown(self):
        NestedModel.drop_collection()

    def test_created_nested_dict(self):
        nstor = NestedModel(dikt={"hello": "world"}).save()
        assert 1 == NestedModel.objects().count()
        assert 1 == NestedModel.objects(dikt__hello="world").count()

        nstor.dikt["hide_me"] = "no"
        nstor.save()
        assert 1 == NestedModel.objects().count()
        assert 1 == NestedModel.objects(dikt__hide_me="no").count()

        nstor.soft_delete()
        assert 0 == NestedModel.objects().count()
        assert 1 == NestedModel.objects().soft_deleted.count()
        assert NestedModel.objects.including_soft_deleted\
                .first().dikt['hide_me'] == 'yes'

        sd_nstor = NestedModel.objects().soft_deleted.first()
        sd_nstor.dikt["hide_me"] = "nope.avi"
        sd_nstor.save()
        sd_nstor.reload()
        assert 1 == NestedModel.objects().count()
