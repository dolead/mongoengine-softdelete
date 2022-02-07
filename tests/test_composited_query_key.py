from tests.base import TestCase

from mongoengine import fields

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class SubQueryModel(SoftDeleteNoCacheDocument):
    meta = {'collection': 'sub_query_model', 'strict': False,
            'soft_delete': {'key': 'deleted'},
    }

    key = fields.StringField()


class TestCompositedSubKeyQuery(TestCase):

    def setUp(self):
        SubQueryModel.drop_collection()

    def tearDown(self):
        SubQueryModel.drop_collection()

    def test_not_overriding_compisited_key(self):
        SubQueryModel(key='deleted').save()
        SubQueryModel(key='knights').save()
        SubQueryModel(key='round table').save()
        SubQueryModel.prout = True
        query = SubQueryModel.objects
        assert query.count() == 2
        assert query.filter(key='knights').count() == 1
        assert query.filter(key__ne='knights').count() == 1
        assert query.filter(key__contains='knights').count() == 1
        assert query.filter(key__ne='deleted').count() == 2
        assert query.filter(key__nin=['deleted']).count() == 2
        assert query.filter(key__in=['knights']).count() == 1
        assert query.filter(key__nin=['knights']).count() == 1

        query = SubQueryModel.objects.including_soft_deleted
        assert query.count() == 3
        assert query.filter(key='knights').count() == 1
        assert query.filter(key__ne='knights').count() == 2
        assert query.filter(key__ne='deleted').count() == 2
        assert query.filter(key__nin=['deleted']).count() == 2
        assert query.filter(key__in=['knights']).count() == 1
        assert query.filter(key__nin=['knights']).count() == 2

        query = SubQueryModel.objects.soft_deleted
        assert query.count() == 1
        assert query.filter(key='knights').count() == 0
        assert query.filter(key__ne='knights').count() == 1
        assert query.filter(key__ne='deleted').count() == 0
        assert query.filter(key__nin=['knights']).count() == 1
        assert query.filter(key__in=['knights']).count() == 0

    def test_composited_key(self):
        model = SubQueryModel(key='knights').save()
        query = SubQueryModel.objects
        assert query.count() == 1
        assert query.filter(key='knights').count() == 1
        assert query.filter(key__ne='deleted').count() == 1
        assert query.filter(key__nin=['deleted']).count() == 1
        assert query.filter(key__in=['knights']).count() == 1

        query = SubQueryModel.objects.including_soft_deleted
        assert query.count() == 1
        assert query.filter(key='knights').count() == 1
        assert query.filter(key__ne='deleted').count() == 1
        assert query.filter(key__nin=['deleted']).count() == 1
        assert query.filter(key__in=['knights']).count() == 1

        query = SubQueryModel.objects(key='knights')
        assert query.filter(key='knights').count() == 1
        assert query.filter(key__ne='deleted').count() == 1
        assert query.filter(key__nin=['deleted']).count() == 1
        assert query.filter(key__in=['knights']).count() == 1

        model.soft_delete()
        assert SubQueryModel.objects.count() == 0
        query = SubQueryModel.objects.soft_deleted
        assert query.count() == 1
        assert query.filter(key='knights').count() == 0
        assert query.filter(key='deleted').count() == 1
        assert query.filter(key__ne='deleted').count() == 0
        assert query.filter(key__nin=['deleted']).count() == 0
        assert query.filter(key__in=['deleted']).count() == 1
