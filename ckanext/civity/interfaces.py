from ckan.plugins.interfaces import Interface


class IFacetLabelFunction(Interface):
    u'''Customize the Label Functions for the facets shown on search pages.

    By implementing this interface plugins can customize the Label Functions for
    the facets that are displayed for filtering search results on the dataset 
    search page, organization pages and group pages.


    The ``label_functions`` passed to each of the functions below is an
    ``Dict`` in which the keys are the package field names and the values
    are the functions that will be used to convert the items show
    interface. For example::

        {'name': label_function_name,
         'description': label_function_descrption}

    If there are multiple ``IFacetLabelFunction`` plugins active at once, each plugin will
    be called (in the order that they're listed in the CKAN config file) and
    they will each be able to modify the label_functions dict in turn.

    '''
    def get_label_functions(self, label_functions):
        u'''Modify and return the ``label_functions`` for the search page.
        Similar to 'get_actions' from IActions interface.

        :param label_functions: the current label_functions dict 
        :type label_functions: Dict

        :returns: the updated ``label_functions``
        :rtype: Dict

        '''
        return label_functions
