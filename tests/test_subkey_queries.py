from datetime import datetime, timedelta
from tests.base import TestCase
from tests.models.photoalbum import Album, Photo

class TestSubKeyQueries(TestCase):
    def setUp(self):
        Photo.drop_collection()
        Album.drop_collection()
        now = datetime.utcnow()
        self.exif = {'GPSInfo': {"GPSVersionID": b'\x02\x03\x00\x00',
                                 "GPSSatellites": '',
                                 "GPSMapDatum": 'WGS-84',
                                 "GPSStatus": 'V'},
                     'ResolutionUnit': 2,
                     'ExifOffset': 360,
                     'Make': 'Canon',
                     'Model': 'Canon EOS 90D',
                     'Artist': '',
                     'Orientation': 1,
                     'DateTime': '2022:01:22 13:05:53',
                     'ApertureValue': 4.375,
                     'Flash': 0,
                     'FocalLength': 35.0,
                     'ExifImageWidth': 4800,
                     'ExifInteroperabilityOffset': 16974,
                     'FocalPlaneXResolution': 5473.204104903079,
                     'FocalPlaneYResolution': 5470.08547008547,
                     'ExifImageHeight': 3200,
                     'FocalPlaneResolutionUnit': 2,
                     'ExposureTime': 0.0125,
                     'FNumber': 4.5,
                     'ISOSpeedRatings': 3200,
                     'ExposureMode': 1,
                     'SensitivityType': 2,
                     'WhiteBalance': 0,
                     'RecommendedExposureIndex': 3200,
                     'LensSpecification': (18.0, 135.0, 0.0, 0.0),
                     'LensModel': 'EF-S18-135mm f/3.5-5.6 IS STM',
                     'MakerNote': b'\x00\x00\x00\x00'}
        self.albums = []
        for album_index in range(1, 4):
            album_date = now + timedelta(days=album_index)
            alb = Album(name=album_date.strftime("%Y-%m-%d"), author="You",
                        created_at=album_date).save()
            for photo_index in range(1, 12):
                photo_date = album_date + timedelta(seconds=photo_index)
                photo_number = photo_index + (12 * (album_index - 1))
                Photo(
                    filepath=f"~/pics/{alb.name}/IMG_{photo_number:05}.jpg",
                    author=alb.author,
                    created_at=photo_date,
                    exif=self.exif,
                    album=alb).save()


    def tearDown(self):
        Photo.drop_collection()
        Album.drop_collection()

    def test_get_album(self):
        assert Album.objects.count() == 3
        for album in Album.objects():
            assert album.photos.count() == 11

        photo = Photo.objects().first()
        assert photo

    def test_contains(self):
        photo = Photo.objects(filepath__contains="IMG_00001.jpg").first()
        assert photo

        photo = Photo.objects(exif__Make="Canon").first()
        assert photo

        photo = Photo.objects(exif__GPSInfo__GPSMapDatum="WGS-84").first()
        assert photo

        photo = Photo.objects(
            exif__GPSInfo__GPSMapDatum__ne="????").first()
        assert photo

    def test_contains_softdeleted(self):
        photo = Photo.objects(filepath__contains="IMG_00001.jpg").first()
        album = photo.album
        photo.soft_delete()
        photo = Photo.objects(filepath__contains="IMG_00001.jpg").first()
        assert not photo

        photos = Photo.objects(exif__GPSInfo__GPSMapDatum="WGS-84")
        assert photos
        photos = Photo.objects(exif__GPSInfo__GPSMapDatum__icontains="wgs")
        assert photos

        for p in photos:
            p.soft_delete()
        photos = Photo.objects(exif__GPSInfo__GPSMapDatum="WGS-84")
        assert not photos
