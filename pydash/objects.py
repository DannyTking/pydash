"""Objects
"""

from __future__ import absolute_import

import copy

from .arrays import flatten
from .utilities import identity
from .utils import iterate, iter_callback, get_item, set_item
from ._compat import (
    iteritems,
    itervalues,
    iterkeys,
    integer_types,
    string_types,
)


def assign(obj, *sources, **kargs):
    """Assigns own enumerable properties of source object(s) to the destination
    object.
    """
    sources = list(sources)
    callback = kargs.get('callback')

    if callback is None and callable(sources[-1]):
        callback = sources.pop()

    for source in sources:
        for key, value in iteritems(source):
            obj[key] = (value if callback is None
                        else callback(obj.get(key), value))

    return obj


extend = assign


def clone(value, is_deep=False, callback=None):
    """Creates a clone of `value`. If `is_deep` is ``True`` nested valueects
    will also be cloned, otherwise they will be assigned by reference. If a
    callback is provided it will be executed to produce the cloned values. The
    callback is invoked with one argument: (value).

    Args:
        value (mixed): dict or list to clone
        is_deep (bool, optional): whether to perform deep clone
        callback (mixed, optional): function that provides cloned values

    Returns:
        mixed: cloned dict or list
    """
    if callback is None:
        callback = identity

    copier = copy.deepcopy if is_deep else copy.copy
    value = copier(value)

    obj = [(key, callback(val)) for key, val in iterate(value)]

    if isinstance(value, list):
        obj = [val for _, val in obj]
    else:
        obj = dict(obj)

    return obj


def clone_deep(value, callback=None):
    """Creates a deep clone of `value`. If a callback is provided it will be
    executed to produce the cloned values. The callback is invoked with one
    argument: (value).

    Args:
        value (mixed): dict or list to clone
        callback (mixed, optional): function that provides cloned values

    Returns:
        dict: cloned dict
    """
    return clone(value, is_deep=True, callback=callback)


def defaults(obj, *sources):
    """Assigns own enumerable properties of source object(s) to the destination
    object for all destination properties that resolve to undefined.
    """
    for source in sources:
        for key, value in iteritems(source):
            obj.setdefault(key, value)

    return obj


def find_key(obj, callback):
    """This method is like :func:`pydash.arrays.find_index` except that it
    returns the key of the first element that passes the callback check,
    instead of the element itself.
    """
    for result, _, key, _ in iter_callback(obj, callback):
        if result:
            return key


find_last_key = find_key


def for_in(obj, callback):
    """Iterates over own and inherited enumerable properties of `obj`,
    executing `callback` for each property.
    """
    for result, _, _, _ in iter_callback(obj, callback):
        if result is False:
            break

    return obj


for_in_right = for_in
for_own = for_in
for_own_right = for_in


def functions_(obj):
    """Creates a list of keys of an object that are callable.
    """
    return [key for key, value in iteritems(obj) if callable(value)]


methods = functions_


def has(obj, key):
    """Checks if `key` exists as a key of `obj`.

    Args:
        obj (mixed): Object to test.
        key (mixed): Key to test for.

    Returns:
        bool: Whether `obj` has `key`.
    """
    return key in [key for key, value in iterate(obj)]


def invert(obj):
    """Creates an object composed of the inverted keys and values of the given
    object.

    Args:
        obj (dict): dict to invert

    Returns:
        dict: Inverted dict

    Note:
        Assumes `dict` values are hashable as `dict` keys.
    """
    return dict((value, key) for key, value in iterate(obj))


def is_list(value):
    """Checks if `value` is a list.
    """
    return isinstance(value, list)


def is_boolean(value):
    """Checks if `value` is a boolean value.
    """
    return isinstance(value, bool)


def is_empty(value):
    """Checks if `value` is empty.
    """
    return any([is_boolean(value), is_number(value), not value])


def is_function(value):
    """Checks if `value` is a function.
    """
    return callable(value)


def is_none(value):
    """Checks if `value` is `None`.
    """
    return value is None


def is_number(value):
    """Checks if `value` is a number.
    """
    return isinstance(value, integer_types + (float,))


def is_string(value):
    """Checks if `value` is a string.
    """
    return isinstance(value, string_types)


def keys(obj):
    """Creates a list composed of the keys of `obj`.

    Args:
        obj (mixed): Object to extract keys from.

    Returns:
        list: List of keys.
    """
    return [key for key, value in iterate(obj)]


def map_values(obj, callback=None):
    """Creates an object with the same keys as `obj` and values generated by
    running each property of `obj` through the `callback`. The callback is
    invoked with three arguments: (value, key, object). If a property name is
    provided for `callback` the created :func:`pluck` style callback will
    return the property value of the given element. If an object is provided
    for callback the created :func:`where` style callback will return `True`
    for elements that have the properties of the given object, else `False`.
    """
    ret = {}

    for result, _, key, _ in iter_callback(obj, callback):
        ret[key] = result

    return ret


def merge(obj, *sources, **kargs):
    """Recursively merges own enumerable properties of the source object(s)
    that don't resolve to undefined into the destination object. Subsequent
    sources will overwrite property assignments of previous sources. If a
    callback is provided it will be executed to produce the merged values of
    the destination and source properties. If the callback returns undefined
    merging will be handled by the method instead. The callback is invoked with
    two arguments: (obj_value, source_value).

    Args:
        obj (dict): destination object to merge source(s) into
        *sources (dict): source objects to merge from. subsequent sources
            overwrite previous ones
        **callback (function, optional): callback function to handle merging
            (must be passed in as keyword argument)

    Returns:
        dict: merged object

    Warning:
        `obj` is modified in place.
    """
    callback = kargs.get('callback')

    for source in sources:
        update(obj, source, callback)

    return obj


def update(obj, source, callback=None):
    """Update properties of `obj` with `source`. If a callback is provided,
    it will be executed to product the updated values of the destination and
    source properties. The callback is invoked with two arguments:
    (obj_value, source_value).

    Args:
        obj (dict): destination object to merge source(s) into
        source (dict): source object to merge from
        callback (function, optional): callback function to handle merging

    Returns:
        mixed: merged object

    Warning:
        `obj` is modified in place.
    """

    for key, src_value in iterate(source):
        obj_value = get_item(obj, key, default=None)
        is_sequences = all([src_value,
                            isinstance(src_value, list),
                            isinstance(obj_value, list)])
        is_mappings = all([src_value,
                           isinstance(src_value, dict),
                           isinstance(obj_value, dict)])

        if (is_sequences or is_mappings) and not callback:
            result = update(obj_value, src_value)
        elif callback:
            result = callback(obj_value, src_value)
        else:
            result = src_value

        set_item(obj, key, result)

    return obj


def omit(obj, callback=None, *properties):
    """Creates a shallow clone of object excluding the specified properties.
    Property names may be specified as individual arguments or as lists of
    property names. If a callback is provided it will be executed for each
    property of object omitting the properties the callback returns truthy for.
    The callback is invoked with three arguments: (value, key, object).

    Args:
        obj (mixed): Object to process.
        *properties (str): Property values to omit.
        callback (mixed, optional): Callback used to determine whic properties
            to omit.

    Returns:
        dict: Results of omitting properties.
    """
    if not callable(callback):
        callback = callback if callback is not None else []
        properties = flatten([callback, properties])
        callback = lambda value, key, item: key in properties

    return dict((key, value) for key, value in iterate(obj)
                if not callback(value, key, obj))


def pairs(obj):
    """Creates a two dimensional list of an object's key-value pairs, i.e.
    [[key1, value1], [key2, value2]].

    Args:
        obj (mixed): Object to process.

    Returns:
        list: Two dimensional list of object's key-value pairs.
    """
    return [[key, value] for key, value in iterate(obj)]


def pick(obj, callback=None, *properties):
    """Creates a shallow clone of object composed of the specified properties.
    Property names may be specified as individual arguments or as lists of
    property names. If a callback is provided it will be executed for each
    property of object picking the properties the callback returns truthy for.
    The callback is invoked with three arguments; (value, key, object).

    Args:
        obj (mixed): Object to pick from.
        *properties (str): Property values to pick.
        callback (mixed, optional): Callback used to determine whic properties
            to pick.

    Returns:
        dict: Results of picking properties.
    """
    if not callable(callback):
        callback = callback if callback is not None else []
        properties = flatten([callback, properties])
        callback = lambda value, key, item: key in properties

    return dict((key, value) for key, value in iterate(obj)
                if callback(value, key, obj))


def transform(obj, callback=None, accumulator=None):
    """An alternative to :func:`reduce`, this method transforms `obj` to a new
    accumulator object which is the result of running each of its properties
    through a callback, with each callback execution potentially mutating the
    accumulator object. The callback is invoked with four arguments:
    (accumulator, value, key, object). Callbacks may exit iteration early by
    explicitly returning `False`.
    """
    if callback is None:
        callback = lambda accumulator, *args: accumulator

    if accumulator is None:
        accumulator = []

    for key, value in iterate(obj):
        result = callback(accumulator, value, key, obj)
        if result is False:
            break

    return accumulator


def values(obj):
    """Creates a list composed of the values of `obj`.

    Args:
        obj (mixed): Object to extract values from.

    Returns:
        list: List of values.
    """
    return [value for key, value in iterate(obj)]
