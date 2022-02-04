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

    def _clean_initial_query_on_conflicting_filter(self, queryset,
                                                   q_obj, query):
        soft_delete_attrs = self._document._meta.get('soft_delete', {})
        sd_bkey_comp = {self.__extract_attr(key): not isinstance(value, str)
                         for key, value in soft_delete_attrs.items()}
        for sd_key, sd_base_filter in list(soft_delete_attrs.items()):
            sd_base_key = self.__extract_attr(sd_key)
            if sd_base_key not in query:
                continue
            if not isinstance(sd_base_filter, str):
                # if base sd filter is complex or a negation => ignore
                continue
            base_key = self.__extract_attr(key)
            comp = base_key != key  # if same => simple cond, otherwise compo
            if base_key not in sd_bkey_comp:
                continue  # nothing to clean
            if sd_bkey_comp[base_key] and comp:
                continue
            if base_key in queryset.initial_query:
                del queryset._query[base_key]

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
        queryset = super().__call__(q_obj=q_obj, **query)
        self._clean_initial_query_on_conflicting_filter(queryset, q_obj, query)
        return queryset

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
        queryset = super().__call__(q_obj=q_obj, **query)
        self._clean_initial_query_on_conflicting_filter(queryset, q_obj, query)
        return queryset

    def no_cache(self):
        return self

    def cache(self):
        return self._clone_into_qs(SoftDeleteQuerySet)

    def __len__(self):
        """Returning the self.count()."""
        return self.count()
