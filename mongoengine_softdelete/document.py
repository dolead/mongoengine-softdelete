from pymongo.read_preferences import ReadPreference

from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.queryset import QuerySet, OperationError
from mongoengine.document import Document

from mongoengine_softdelete import signals
from mongoengine_softdelete.queryset import (SoftDeleteQuerySet,
                                             SoftDeleteQuerySetNoCache)


class AbstactSoftDeleteDocument(Document):
    meta = {'abstract': True}

    def soft_delete(self):
        """Won't delete the document as much as marking it as deleted according
        to parameters present in meta.
        """
        signals.pre_soft_delete.send(self.__class__, document=self)
        for key, val in self._meta.get('soft_delete', {}).items():
            setattr(self, key, val)
        self.save()
        signals.post_soft_delete.send(self.__class__, document=self)

    def soft_undelete(self):
        """Will undelete the document
        """
        signals.pre_soft_undelete.send(self.__class__, document=self)
        for key in self._meta.get('soft_delete', {}):
            undelete_value = self._fields[key].default
            setattr(self, key, undelete_value)
        self.save()
        signals.post_soft_undelete.send(self.__class__, document=self)

    @property
    def is_soft_deleted(self):
        """Return true if the field of the document are set according to the
        soft deleted state as defined in the metas.
        """
        for key in self._meta.get('soft_delete', {}):
            if not self._meta['soft_delete'][key] == getattr(self, key):
                return False
        return True

    def update(self, **kwargs):
        """The ~mongoengine.Document.update method had to be overriden
        so it's not soft_delete aware and will update document
        no matter the "soft delete" state.
        """
        old_qs = self._qs
        setattr(self, '__objects', old_qs.including_soft_deleted)
        try:
            res = super().update(**kwargs)
        except:
            raise
        finally:
            setattr(self, '__objects', old_qs)
        return res

    def reload(self, *fields, **kwargs):
        """Overriding reload which would raise DoesNotExist
        on soft deleted document"""
        old_qs = self._qs
        setattr(self, '__objects', old_qs.including_soft_deleted)
        try:
            res = super().reload(*fields, **kwargs)
        except:
            raise
        finally:
            setattr(self, '__objects', old_qs)
        return res


class SoftDeleteDocument(AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySet, 'abstract': True}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass


class SoftDeleteNoCacheDocument(AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySetNoCache, 'abstract': True}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass
