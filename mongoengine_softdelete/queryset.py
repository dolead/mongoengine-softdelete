from mongoengine.queryset import QuerySet, QuerySetNoCache
from mongoengine.queryset.transform import (COMPARISON_OPERATORS,
                                            STRING_OPERATORS)


class AbstractSoftDeleteMixin:
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

    def _clean_initial_query_on_conflicting_filter(self, query):
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        soft_delete_keys = {self.__extract_attr(k) for k in soft_delete_attrs}
        for key in query:
            base_key = self.__extract_attr(key)
            if base_key in soft_delete_keys and base_key in self.initial_query:
                del self.initial_query[base_key]

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

    def _clone_into_qs(self, NewCls):
        qs = NewCls(self._document, self._collection)
        # being resilient to upstream attribute rename
        method = getattr(self, '_clone_into') if hasattr(self, '_clone_into') \
            else getattr(self, 'clone_into')
        return method(qs)


class SoftDeleteQuerySet(QuerySet, AbstractSoftDeleteMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        not_soft_deleted_conditions = self._not_soft_deleted_cond(**kwargs)
        self.initial_query.update(not_soft_deleted_conditions)

    def __call__(self, q_obj=None, **query):
        self._clean_initial_query_on_conflicting_filter(query)
        return super().__call__(q_obj=q_obj, **query)

    def cache(self):
        return self

    def no_cache(self):
        return self._clone_into_qs(SoftDeleteQuerySetNoCache)


class SoftDeleteQuerySetNoCache(QuerySetNoCache, AbstractSoftDeleteMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        not_soft_deleted_conditions = self._not_soft_deleted_cond(**kwargs)
        self.initial_query.update(not_soft_deleted_conditions)

    def __call__(self, q_obj=None, **query):
        self._clean_initial_query_on_conflicting_filter(query)
        return super().__call__(q_obj=q_obj, **query)

    def no_cache(self):
        return self

    def cache(self):
        return self._clone_into_qs(SoftDeleteQuerySet)

    def __len__(self):
        """Returning the self.count()."""
        return self.count()
