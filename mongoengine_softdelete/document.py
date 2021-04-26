from pymongo.read_preferences import ReadPreference

from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.queryset import QuerySet, OperationError
from mongoengine.document import Document

from mongoengine_softdelete import signals
from mongoengine_softdelete.queryset import (SoftDeleteQuerySet,
                                             SoftDeleteQuerySetNoCache)


class AbstactSoftDeleteDocument:

    @property
    def _qs(self):  # FIXME should be present in mongoengine ?
        """Returns the queryset to use for updating / reloading / deletions."""
        if not hasattr(self, '__objects'):
            queryset_class = self._meta.get('queryset_class', QuerySet)
            self.__objects = queryset_class(self, self._get_collection())
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
        if not self.pk:
            if kwargs.get('upsert', False):
                query = self.to_mongo()
                if "_cls" in query:
                    del (query["_cls"])
                return self._qs.including_soft_deleted \
                    .filter(**query).update_one(**kwargs)
            else:
                raise OperationError('attempt to update a document not yet '
                                     'saved')
        return self._qs.including_soft_deleted \
            .filter(**self._object_key).update_one(**kwargs)

    def reload(self, max_depth=1):
        """Overriding reload.

        Overriding reload which would raise DoesNotExist
        on soft deleted document
        """
        if not self.pk:
            raise self.DoesNotExist("Document does not exist")
        obj = self._qs.read_preference(ReadPreference.PRIMARY) \
            .filter(**self._object_key).including_soft_deleted.limit(1) \
            .select_related(max_depth=max_depth)

        if obj:
            obj = obj[0]
        else:
            raise self.DoesNotExist("Document does not exist")
        for field in self._fields_ordered:
            setattr(self, field, self._reload(field, obj[field]))
        self._changed_fields = obj._changed_fields
        self._created = False
        return obj


class SoftDeleteDocument(Document, AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySet}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass


class SoftDeleteNoCacheDocument(Document, AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySetNoCache}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass
