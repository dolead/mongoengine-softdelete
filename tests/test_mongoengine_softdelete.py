import pytest

from mongoengine import connect

from tests.models.icecream import IceCream

class TestCase:
    @staticmethod
    @pytest.fixture(autouse=True)
    def _database():
        db = connect(db="mongoengine_softdelete")
        TestCase.setUp()
        yield
        TestCase.tearDown()
        db.close()

    @staticmethod
    def setUp():
        IceCream.drop_collection()

    @staticmethod
    def tearDown():
        IceCream.drop_collection()

    @staticmethod
    def test_create_icecream():
        icecreams = IceCream.objects
        assert icecreams.count() == 0

        ice = IceCream(flavor="Vanilla", color="White")
        assert not ice.id
        assert ice.color == "White"

        ice = ice.save()
        assert ice.id

        icecreams = IceCream.objects()
        assert icecreams.count() == 1

    @staticmethod
    def test_soft_delete():
        ice = IceCream(flavor="Strawberry", color="Red").save()
        assert ice.id
        assert IceCream.objects().count() > 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() == 0
        assert not ice.is_soft_deleted

        ice.soft_delete()
        ice = ice.reload()
        assert IceCream.objects().count() == 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() > 0
        assert ice.is_soft_deleted

        ice.soft_undelete()
        assert IceCream.objects().count() > 0
        assert IceCream.objects().including_soft_deleted.count() > 0
        assert IceCream.objects().soft_deleted.count() == 0
        assert not ice.is_soft_deleted
