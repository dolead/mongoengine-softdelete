from tests.base import TestCase
from tests.models.nested import Nestor


class TestSubKeyQueries(TestCase):
    def setUp(self):
        Nestor.drop_collection()

    def tearDown(self):
        Nestor.drop_collection()

    def test_created_nested_dict(self):
        nstor = Nestor(dikt={"hello": "world"}).save()
        assert 1 == Nestor.objects().count()

        nstor.dikt["hide_me"] = "maybe"
        nstor.save()
        assert 1 == Nestor.objects().count()

        nstor.soft_delete()
        assert 0 == Nestor.objects().count()
        assert 1 == Nestor.objects().soft_deleted.count()

        sd_nstor = Nestor.objects().soft_deleted.first()
        sd_nstor.dikt["hide_me"] = "nope.avi"
        sd_nstor.save()
        sd_nstor.reload()
        assert 1 == Nestor.objects().count()
