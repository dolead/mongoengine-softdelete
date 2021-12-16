from pymongo.read_preferences import ReadPreference

from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.queryset import QuerySet, OperationError
from mongoengine.document import Document

from mongoengine_softdelete import signals
from mongoengine_softdelete.queryset import (SoftDeleteQuerySet,
                                             SoftDeleteQuerySetNoCache)


class AbstactSoftDeleteDocument(Document):
    meta = {'abstract': True}

    @property
    def _qs(self):
        """Return the default queryset corresponding to this document."""
        if not hasattr(self, "__objects"):
            queryset_class = self._meta.get("queryset_class", QuerySet)
            self.__objects = queryset_class(self.__class__, self._get_collection())
        return self.__objects

    def soft_delete(self):
        """Soft delete a document.

        Marks a document as deleted based on the parameter set in meta instead
        of deleting it.
        """
        signals.pre_soft_delete.send(self.__class__, document=self)
        for key, val in self._meta.get('soft_delete', {}).items():
            setattr(self, key, val)
        self.save()
        signals.post_soft_delete.send(self.__class__, document=self)

    def soft_undelete(self):
        """Will undelete the document."""
        signals.pre_soft_undelete.send(self.__class__, document=self)
        for key in self._meta.get('soft_delete', {}):
            undelete_value = self._fields[key].default
            setattr(self, key, undelete_value)
        self.save()
        signals.post_soft_undelete.send(self.__class__, document=self)

    @property
    def is_soft_deleted(self):
        """Check if the document is soft deleted.

        Return true if the field of the document are set according to the
        soft deleted state as defined in the metas.
        """
        for key in self._meta.get('soft_delete', {}):
            if not self._meta['soft_delete'][key] == getattr(self, key):
                return False
        return True

    def update(self, **kwargs):
        """Overriding  ~mongoengine.Document.update method.

        The ~mongoengine.Document.update method had to be overriden
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
