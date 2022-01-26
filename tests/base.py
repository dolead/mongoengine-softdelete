import pytest

from mongoengine import connect


class TestCase:
    @pytest.fixture(autouse=True)
    def _database(self):
        db = connect(db="mongoengine_softdelete")
        self.setUp()
        yield
        self.tearDown()
        db.close()

    def setUp(self):
        pass

    def tearDown(self):
        pass
