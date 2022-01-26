from tests.base import TestCase
from tests.models.icecream import IceCream


class TestSoftDelete(TestCase):
    def setUp(self):
        IceCream.drop_collection()

    def tearDown(self):
        IceCream.drop_collection()

    def test_create_icecream(self):
        icecreams = IceCream.objects
        assert icecreams.count() == 0

        ice = IceCream(flavor="Vanilla", color="White")
        assert not ice.id
        assert ice.color == "White"

        ice = ice.save()
        assert ice.id

        icecreams = IceCream.objects()
        assert icecreams.count() == 1

    def test_soft_delete(self):
        ice = IceCream(flavor="Strawberry", color="Red").save()
        assert ice.id
        assert IceCream.objects().count() > 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() == 0
        assert not ice.is_soft_deleted

        ice.soft_delete()
        ice.reload()
        assert IceCream.objects().count() == 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() > 0
        assert ice.is_soft_deleted

        ice.soft_undelete()
        ice.reload()
        assert IceCream.objects().count() > 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() == 0
        assert not ice.is_soft_deleted
