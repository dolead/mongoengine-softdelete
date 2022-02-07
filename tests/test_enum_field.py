from tests.base import TestCase
from pytest import skip
from enum import Enum

from mongoengine import fields, VERSION

from mongoengine_softdelete.document import SoftDeleteNoCacheDocument


class Status(Enum):
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    PAUSED = 'PAUSED'


class TestNestedSubKeyQueries(TestCase):

    def setUp(self):
        if VERSION[0] < 1 and VERSION[1] < 21:
            skip("Mongoengine < 0.21 doesn't support EnumField, skipping")

        class Model(SoftDeleteNoCacheDocument):
            meta = {'collection': 'model', 'strict': False,
                    'soft_delete': {'status': Status.DELETED}}

            status = fields.EnumField(Status)

        self.ModelCls = Model
        self.ModelCls.drop_collection()

    def test_sd_enum_value(self):
        self.ModelCls(status='DELETED').save()
        self.ModelCls(status='PAUSED').save()
        self.ModelCls(status='ACTIVE').save()
        assert self.ModelCls.objects.count() == 2
        assert self.ModelCls.objects(status__ne='ACTIVE').count() == 1
        assert self.ModelCls.objects(status__ne='ACTIVE').filter(
            status__ne='PAUSED').count() == 0
        assert self.ModelCls.objects(status__ne='ACTIVE').filter(
            status__ne='PAUSED').including_soft_deleted.count() == 1
        assert self.ModelCls.objects(
            status__ne='ACTIVE').including_soft_deleted.filter(
            status__ne='PAUSED').including_soft_deleted.count() == 1
        assert self.ModelCls.objects(
            status__ne='ACTIVE').including_soft_deleted.filter(
            status__ne='PAUSED').including_soft_deleted\
            .soft_deleted.count() == 1

    def test_sd_enum_instance(self):
        self.ModelCls(status='DELETED').save()
        self.ModelCls(status='PAUSED').save()
        self.ModelCls(status='ACTIVE').save()
        assert self.ModelCls.objects.count() == 2
        assert self.ModelCls.objects(status__ne=Status.ACTIVE).count() == 1
        assert self.ModelCls.objects(status__ne=Status.ACTIVE).filter(
            status__ne=Status.PAUSED).count() == 0
        assert self.ModelCls.objects(status__ne=Status.ACTIVE).filter(
            status__ne=Status.PAUSED).including_soft_deleted.count() == 1
        assert self.ModelCls.objects(
            status__ne=Status.ACTIVE).including_soft_deleted.filter(
            status__ne=Status.PAUSED).including_soft_deleted.count() == 1
        assert self.ModelCls.objects(
            status__ne=Status.ACTIVE).including_soft_deleted.filter(
            status__ne=Status.PAUSED).including_soft_deleted\
            .soft_deleted.count() == 1
        assert self.ModelCls.objects.including_soft_deleted.filter(
            status=Status.DELETED).count() == 1

    def tearDown(self):
        self.ModelCls.drop_collection()
