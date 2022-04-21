from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.utils.encoding import force_text

from .classes import SearchBackend, SearchModel
from .exceptions import DynamicSearchException
from .literals import QUERY_PARAMETER_ANY_FIELD, SEARCH_MODEL_NAME_KWARG


class SearchEnabledListViewMixin:
    search_disable_list_filtering = False

    def get_search_model(self, queryset):
        try:
            model = queryset.model
        except AttributeError:
            return
        else:
            try:
                return SearchModel.get_for_model(instance=model)
            except KeyError:
                return

    def get_context_data(self):
        context = super().get_context_data()

        if not self.search_disable_list_filtering:
            queryset = super().get_queryset()

            search_model = self.get_search_model(queryset=queryset)
            if search_model:
                context.update(
                    {
                        'search_model': search_model
                    }
                )

                query_dict = self.request.GET.copy()
                query_dict.update(self.request.POST)

                if (QUERY_PARAMETER_ANY_FIELD in query_dict) and query_dict[QUERY_PARAMETER_ANY_FIELD].strip():
                    context.update(
                        {'filter_terms': query_dict[QUERY_PARAMETER_ANY_FIELD].strip()}
                    )

        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.search_disable_list_filtering:
            search_model = self.get_search_model(queryset=queryset)
            if search_model:
                query_dict = self.request.GET.copy()
                query_dict.update(self.request.POST)

                if query_dict.get('_match_all', 'off').lower() in ['on', 'true']:
                    global_and_search = True
                else:
                    global_and_search = False

                if query_dict.get(QUERY_PARAMETER_ANY_FIELD, '').strip():
                    try:
                        search_queryset = SearchBackend.get_instance().search(
                            global_and_search=global_and_search,
                            search_model=search_model,
                            query=query_dict, user=self.request.user
                        )
                    except DynamicSearchException as exception:
                        if settings.DEBUG or settings.TESTING:
                            raise

                        messages.error(message=exception, request=self.request)
                        return search_model.model._meta.default_manager.none()
                    else:
                        return queryset.filter(pk__in=search_queryset)
                else:
                    return queryset
            else:
                return queryset
        else:
            return queryset


class SearchModelViewMixin:
    def dispatch(self, *args, **kwargs):
        self.search_model = self.get_search_model()
        return super().dispatch(*args, **kwargs)

    def get_search_model_name(self):
        search_model_name = self.kwargs.get(
            SEARCH_MODEL_NAME_KWARG, self.request.GET.get(
                '_{}'.format(SEARCH_MODEL_NAME_KWARG), self.request.POST.get(
                    '_{}'.format(SEARCH_MODEL_NAME_KWARG)
                )
            )
        )

        if search_model_name:
            search_model_name = search_model_name.lower()

        return search_model_name

    def get_search_model(self):
        try:
            return SearchModel.get(name=self.get_search_model_name())
        except KeyError as exception:
            raise Http404(force_text(s=exception))
