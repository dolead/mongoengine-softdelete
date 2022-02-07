from pymongo.read_preferences import ReadPreference

from mongoengine.base import TopLevelDocumentMetaclass
from mongoengine.queryset import QuerySet, OperationError, queryset_manager
from mongoengine.document import Document

from mongoengine_softdelete import signals
from mongoengine_softdelete.queryset import (SoftDeleteQuerySet,
                                             SoftDeleteQuerySetNoCache)


class AbstactSoftDeleteDocument(Document):
    meta = {'abstract': True}

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

    def _sd_objects(self, queryset):
        soft_delete_attrs = self._meta.get('soft_delete', {})
        QuerySetCls = self._meta['queryset_class']
        for field, sd_value in soft_delete_attrs.items():
            queryset = queryset.filter(**{field + '__ne': sd_value})
        return queryset._clone_into(QuerySetCls(self, self._get_collection()))


class SoftDeleteDocument(AbstactSoftDeleteDocument):
    meta = {'abstract': True, 'queryset_class': SoftDeleteQuerySet}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass

    @queryset_manager
    def objects(self, queryset):
        # set at metaclass, hence the double self
        return self._sd_objects(self, queryset)


class SoftDeleteNoCacheDocument(AbstactSoftDeleteDocument):
    meta = {'abstract': True, 'queryset_class': SoftDeleteQuerySetNoCache}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass

    @queryset_manager
    def objects(self, queryset):
        # set at metaclass, hence the double self
        return self._sd_objects(self, queryset)
