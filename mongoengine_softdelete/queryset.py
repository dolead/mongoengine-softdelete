from mongoengine.queryset import QuerySet, QuerySetNoCache, transform
from mongoengine import Q
from mongoengine.queryset.transform import (COMPARISON_OPERATORS,
                                            STRING_OPERATORS)


class AbstractSoftDeleteMixin:

    def _sd_init(self):
        self._sd_initial_query.update(self._not_soft_deleted_cond())
        self._query_obj &= Q(**self._sd_initial_query)

    def __to_mongo(self, key, val):
        return self._document._fields[key].to_mongo(val)

    @staticmethod
    def __extract_attr(key):
        for operator in COMPARISON_OPERATORS + STRING_OPERATORS:
            if key.endswith(f'__{operator}'):
                key = key[:-(len(f'__{operator}'))]
                if key.endswith('__not'):
                    return key[:-len('__not')]
                return key
        return key

    @property
    def _sd_initial_query(self):
        """Handling deprecated and renamed field"""
        try:
            return self._initial_query
        except AttributeError:
            return self._cls_query

    def _not_soft_deleted_cond(self):
        """Query conditions for documents that are not soft deleted."""
        cond = {}
        for key, val in self._document._meta.get('soft_delete', {}).items():
            if isinstance(val, bool):
                cond[key] = not val
            else:
                cond[key] = {'$ne': self.__to_mongo(key, val)}
        return cond

    @property
    def including_soft_deleted(self):
        """Will clean the queryset from soft_delete notions."""
        qs = self.clone()
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        for key in set(qs._sd_initial_query).intersection(soft_delete_attrs):
            qs._sd_initial_query.pop(key)
        for key in set(qs._query_obj.query).intersection(soft_delete_attrs):
            qs._query_obj.query.pop(key)
        return qs

    @property
    def soft_deleted(self):
        """Will include in the queryset only soft deleted documents."""
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        qs = self.including_soft_deleted.clone()
        for field, sd_value in soft_delete_attrs.items():
            qs = qs.filter(**{field: self.__to_mongo(field, sd_value)})
        return qs

    def _clone_into_qs(self, NewCls):
        qs = NewCls(self._document, self._collection)
        # being resilient to upstream attribute rename
        method = getattr(self, '_clone_into') if hasattr(self, '_clone_into') \
            else getattr(self, 'clone_into')
        return method(qs)


class SoftDeleteQuerySet(QuerySet, AbstractSoftDeleteMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sd_init()

    def cache(self):
        return self

    def no_cache(self):
        return self._clone_into_qs(SoftDeleteQuerySetNoCache)

    def __call__(self, q_obj=None, **query):
        query = transform.query(**query)
        return super().__call__(q_obj, **query)


class SoftDeleteQuerySetNoCache(QuerySetNoCache, AbstractSoftDeleteMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sd_init()

    def __call__(self, q_obj=None, **query):
        query = transform.query(**query)
        return super().__call__(q_obj, **query)

    def no_cache(self):
        return self

    def cache(self):
        return self._clone_into_qs(SoftDeleteQuerySet)
