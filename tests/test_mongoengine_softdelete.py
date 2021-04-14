import pytest

from mongoengine import connect

from tests.models.icecream import IceCream

class TestCase:
    @pytest.fixture(autouse=True)
    def _database(self):
        db = connect(db="mongoengine_softdelete")
        self.setUp()
        yield
        self.tearDown()
        db.close()

    def setUp(self):
        IceCream.drop_collection()

    def tearDown(self):
        IceCream.drop_collection()

    def test_create_icecream(self):
        icecreams = IceCream.objects
        assert len(icecreams) == 0

        ice = IceCream(flavor="Vanilla", color="White")
        assert not ice.id
        assert ice.color == "White"

        ice = ice.save()
        assert ice.id

        icecreams = IceCream.objects()
        assert len(icecreams) == 1

    def test_soft_delete(self):
        ice = IceCream(flavor="Strawberry", color="Red").save()
        assert ice.id
        assert len(IceCream.objects()) > 0
        assert len(IceCream.objects(deleted=True)) == 0
        assert not ice.is_soft_deleted

        ice.soft_delete()
        ice = ice.reload()
        assert len(IceCream.objects()) == 0
        assert len(IceCream.objects(deleted=True)) > 0
        assert ice.is_soft_deleted

        ice.soft_undelete()
        assert len(IceCream.objects()) > 0
        assert len(IceCream.objects(deleted=True)) == 0
        assert not ice.is_soft_deleted
