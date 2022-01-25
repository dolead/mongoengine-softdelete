from tests.base import TestCase
from tests.models.nested import Nested

class TestSubKeyQueries(TestCase):
    def setUp(self):
        Nested.drop_collection()

    def tearDown(self):
        Nested.drop_collection()

    def test_created_nested_dict(self):
        nstor = Nested(dikt={"hello": "world"}).save()
        assert 1 == Nested.objects().count()

        nstor.dikt["hide_me"] = "maybe"
        nstor.save()
        assert 1 == Nested.objects().count()

        nstor.dikt["hide_me"] = "yes"
        nstor.save()
        assert 0 == Nested.objects().count()
