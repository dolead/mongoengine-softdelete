from tests.base import TestCase
from tests.models.softcream import SoftCream


class TestSoftDelete(TestCase):
    def setUp(self):
        SoftCream.drop_collection()

    def tearDown(self):
        SoftCream.drop_collection()

    def test_create_softcream(self):
        assert SoftCream.objects().count() == 0

        soft = SoftCream(flavor="Vanilla", color="White")
        assert not soft.id
        assert soft.color == "White"

        soft = soft.save()
        assert soft.id

        assert SoftCream.objects().count() == 1

    def test_soft_delete(self):
        soft = SoftCream(flavor="Strawberry", color="Red").save()
        assert soft.id
        assert SoftCream.objects().count() > 0
        assert SoftCream.objects().including_soft_deleted.count() > 0
        assert SoftCream.objects().soft_deleted.count() == 0
        assert not soft.is_soft_deleted

        soft.soft_delete()
        soft.reload()
        assert SoftCream.objects().count() == 0
        assert SoftCream.objects().including_soft_deleted.count() > 0
        assert SoftCream.objects().soft_deleted.count() > 0
        assert soft.is_soft_deleted

        soft.soft_undelete()
        soft.reload()
        assert SoftCream.objects().count() > 0
        assert SoftCream.objects().including_soft_deleted.count() > 0
        assert SoftCream.objects().soft_deleted.count() == 0
        assert not soft.is_soft_deleted
