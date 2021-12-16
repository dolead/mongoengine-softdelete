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

    def reload(self, *fields, **kwargs):
        """Overriding reload which would raise DoesNotExist
        on soft deleted document"""
        max_depth = 1
        if fields and isinstance(fields[0], int):
            max_depth = fields[0]
            fields = fields[1:]
        elif "max_depth" in kwargs:
            max_depth = kwargs["max_depth"]

        if self.pk is None:
            raise self.DoesNotExist("Document does not exist")

        obj = (
            self._qs.read_preference(ReadPreference.PRIMARY)
            .filter(**self._object_key)
            .only(*fields)
            .limit(1)
            .select_related(max_depth=max_depth)
        )

        if obj:
            obj = obj[0]
        else:
            raise self.DoesNotExist("Document does not exist")
        for field in obj._data:
            if not fields or field in fields:
                try:
                    setattr(self, field, self._reload(field, obj[field]))
                except (KeyError, AttributeError):
                    try:
                        # If field is a special field, e.g. items is stored as _reserved_items,
                        # a KeyError is thrown. So try to retrieve the field from _data
                        setattr(self, field, self._reload(field, obj._data.get(field)))
                    except KeyError:
                        # If field is removed from the database while the object
                        # is in memory, a reload would cause a KeyError
                        # i.e. obj.update(unset__field=1) followed by obj.reload()
                        delattr(self, field)

        self._changed_fields = (
            list(set(self._changed_fields) - set(fields))
            if fields
            else obj._changed_fields
        )
        self._created = False
        return self


class SoftDeleteDocument(AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySet, 'abstract': True}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass


class SoftDeleteNoCacheDocument(AbstactSoftDeleteDocument):
    meta = {'queryset_class': SoftDeleteQuerySetNoCache, 'abstract': True}
    my_metaclass = TopLevelDocumentMetaclass
    __metaclass__ = TopLevelDocumentMetaclass
