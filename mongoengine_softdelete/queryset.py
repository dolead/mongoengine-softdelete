from itertools import chain

from mongoengine.queryset import QuerySet, QuerySetNoCache
from mongoengine.queryset.transform import (COMPARISON_OPERATORS,
                                            STRING_OPERATORS)


class AbstractSoftDeleteMixin:
    def __to_mongo(self, key, val):
        return self._document._fields[key].to_mongo(val)

    @property
    def initial_query(self):
        try:
            return self._initial_query
        except AttributeError:  # Field has been renammed.
            return self._cls_query

    def _not_soft_deleted_cond(self, **kwargs):
        """Query conditions for documents that are not soft deleted."""
        cond = {}
        for key, val in self._document._meta.get('soft_delete', {}).items():
            if key in kwargs:  # not overriding kwargs
                continue
            if isinstance(val, bool):
                cond[key] = not val
            else:
                cond[key] = {'$ne': self.__to_mongo(key, val)}
        return cond

    @property
    def including_soft_deleted(self):
        """Will clean the queryset from soft_delete notions."""
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        for key in set(self.initial_query).intersection(soft_delete_attrs):
            del self.initial_query[key]
        return self.clone()

    @property
    def soft_deleted(self):
        """Will include in the queryset only soft deleted documents."""
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        for field, sd_value in soft_delete_attrs.items():
            self.initial_query[field] = self.__to_mongo(field, sd_value)
        return self.clone()


class SoftDeleteQuerySet(QuerySet, AbstractSoftDeleteMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        not_soft_deleted_conditions = self._not_soft_deleted_cond(**kwargs)
        self.initial_query.update(not_soft_deleted_conditions)

    @staticmethod
    def __extract_attr(key):
        for operator in chain(COMPARISON_OPERATORS, STRING_OPERATORS):
            if key.endswith(f'__{operator}'):
                key = key[:-(len(f'__{operator}'))]
                if key.endswith('__not'):
                    return key[:-len('__not')]
                return key
        return key

    def __call__(self, q_obj=None, **query):
        """Wrapper for ~mongoengine.queryset.QuerySet.__call__.

        A simple wrapper around ~mongoengine.queryset.QuerySet.__call__ that
        allows query parameters to override those written in the initial query.
        """
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        soft_delete_keys = {self.__extract_attr(k) for k in soft_delete_attrs}
        query_keys = {self.__extract_attr(k) for k in query}
        for key in query_keys.intersection(soft_delete_keys):
            del self.initial_query[key]
        return super().__call__(q_obj=q_obj, **query)

    def cache(self):
        return self

    def no_cache(self):
        if hasattr(self, '_clone_into'):   # Renamed in latest MongoEngine
            return self._clone_into(SoftDeleteQuerySetNoCache(
                self._document,
                self._collection))
        return self.clone_into(SoftDeleteQuerySetNoCache(self._document,
                                                         self._collection))


class SoftDeleteQuerySetNoCache(QuerySetNoCache, AbstractSoftDeleteMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        not_soft_deleted_conditions = self._not_soft_deleted_cond(**kwargs)
        self.initial_query.update(not_soft_deleted_conditions)

    def __call__(self, q_obj=None, **query):
        """
        Wrapper for ~mongoengine.queryset.QuerySet.__call__.

        A simple wrapper around ~mongoengine.queryset.QuerySet.__call__ that
        allows query parameters to override those written in the initial query.
        """
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        for key in set(query).intersection(soft_delete_attrs):
            del self.initial_query[key]
        return super().__call__(q_obj=q_obj, **query)

    def no_cache(self):
        return self

    def cache(self):
        if hasattr(self, '_clone_into'):  # Renamed in latest MongoEngine
            return self._clone_into(SoftDeleteQuerySetNoCache(
                self._document,
                self._collection))
        return self.clone_into(SoftDeleteQuerySetNoCache(
            self._document,
            self._collection))

    def __len__(self):
        """Returning the self.count()."""
        return self.count()
