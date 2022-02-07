from mongoengine.queryset import QuerySet, QuerySetNoCache


class AbstractSoftDeleteMixin:

    @property
    def _sd_initial_query(self):
        try:
            return self._initial_query
        except AttributeError:  # Field has been renammed.
            return self._cls_query

    @property
    def including_soft_deleted(self):
        """Will clean the queryset from soft_delete notions."""
        qs = self.clone()
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        def clean_query_obj(query_obj):
            query = getattr(query_obj, 'query', {})
            for key in soft_delete_attrs:
                query.pop(key + '__ne', None)
                self._sd_initial_query.pop(key + '__ne', None)
            for child_query_obj in getattr(query_obj, 'children', []):
                clean_query_obj(child_query_obj)
        clean_query_obj(qs._query_obj)
        return qs

    @property
    def soft_deleted(self):
        """Will include in the queryset only soft deleted documents."""
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        queryset = self.including_soft_deleted.clone()
        return queryset.filter(**soft_delete_attrs)


class SoftDeleteQuerySet(QuerySet, AbstractSoftDeleteMixin):

    def cache(self):
        return self

    def no_cache(self):
        return self._clone_into_qs(SoftDeleteQuerySetNoCache)

    def __len__(self):
        return self.count()


class SoftDeleteQuerySetNoCache(QuerySetNoCache, AbstractSoftDeleteMixin):

    def no_cache(self):
        return self

    def cache(self):
        return self._clone_into_qs(SoftDeleteQuerySet)

    def __len__(self):
        return self.count()
