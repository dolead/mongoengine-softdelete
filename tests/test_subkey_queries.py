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
                     'YCbCrPositioning': 2,
                     'Copyright': '',
                     'XResolution': 72.0,
                     'YResolution': 72.0,
                     'ExifVersion': b'0231',
                     'ComponentsConfiguration': b'\x01\x02\x03\x00',
                     'ShutterSpeedValue': 6.375,
                     'DateTimeOriginal': '2022:01:22 13:05:53',
                     'DateTimeDigitized': '2022:01:22 13:05:53',
                     'ApertureValue': 4.375,
                     'ExposureBiasValue': 0.0,
                     'MeteringMode': 5,
                     'UserComment': b'\x00\x00\x00\x00',
                     'Flash': 0,
                     'FocalLength': 35.0,
                     'ColorSpace': 1,
                     'ExifImageWidth': 4800,
                     'ExifInteroperabilityOffset': 16974,
                     'FocalPlaneXResolution': 5473.204104903079,
                     'FocalPlaneYResolution': 5470.08547008547,
                     'OffsetTime': '+02:00',
                     'OffsetTimeOriginal': '+02:00',
                     'OffsetTimeDigitized': '+02:00',
                     'SubsecTime': '08',
                     'SubsecTimeOriginal': '08',
                     'SubsecTimeDigitized': '08',
                     'ExifImageHeight': 3200,
                     'FocalPlaneResolutionUnit': 2,
                     'ExposureTime': 0.0125,
                     'FNumber': 4.5,
                     'ExposureProgram': 1,
                     'CustomRendered': 0,
                     'ISOSpeedRatings': 3200,
                     'ExposureMode': 1,
                     'FlashPixVersion': b'0100',
                     'SensitivityType': 2,
                     'WhiteBalance': 0,
                     'RecommendedExposureIndex': 3200,
                     'CameraOwnerName': '',
                     'BodySerialNumber': '133713371337',
                     'LensSpecification': (18.0, 135.0, 0.0, 0.0),
                     'LensModel': 'EF-S18-135mm f/3.5-5.6 IS STM',
                     'LensSerialNumber': '000001337a',
                     'SceneCaptureType': 0,
                     'MakerNote': b'\x00\x00\x00\x00'}
        self.albums = []
        for album_index in range(1, 10):
            album_date = now + timedelta(days=album_index)
            alb = Album(name=album_date.strftime("%Y-%m-%d"), author="You",
                        created_at=album_date)
            for photo_index in range(1, 33):
                photo_date = album_date + timedelta(seconds=photo_index)
                photo_number = photo_index + (33 * (album_index - 1))
                alb.photos.append(Photo(
                    filepath=f"~/pics/{alb.name}/IMG_{photo_number:05}.jpg",
                    author=alb.author,
                    created_at=photo_date,
                    exif=self.exif).save())
            alb.save()
            # self.albums.append(alb)


    def tearDown(self):
        Photo.drop_collection()
        Album.drop_collection()

    def test_get_album(self):
        assert Album.objects.count() == 9
        for album in Album.objects():
            assert len(album.photos) == 32

        photo = Album.objects(photos__filepath='~/pics/2022-01-26/IMG_00001.jpg').first()
        assert photo
