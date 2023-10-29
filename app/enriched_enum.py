from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from functools import partial
from typing import Any, Dict, List
import six


class NotFound(ValueError):
    """
    Raised if an enum matching the specifications is not found
    """
    pass

class MultipleFound(ValueError):
    """
    Raised if more than one enum matching the specifications is found
    """
    pass

class EnumItemMeta(type):
    def __instancecheck__(cls, inst):
        """Implement isinstance(inst, cls)."""
        return any(cls.__subclasscheck__(c)
                   for c in {type(inst), inst.__class__})

    def __subclasscheck__(cls, sub):
        """Implement issubclass(sub, cls)."""
        candidates = cls.__dict__.get("__subclass__", set()) | {cls}
        return any(c in candidates for c in sub.mro())

class EnumItem(object):
    def _update_defaults(self, default_attributes):
        for key, value in six.iteritems(default_attributes):
            # Only set attributes that don't already have a value
            if not hasattr(self, key):
                setattr(self, key, value)


def setUpItem(obj, value, label, **kwargs):
    obj.value = value
    obj.label = label
    for key, value in six.iteritems(kwargs):
        setattr(obj, key, value) 

class EnumIntItem(EnumItem, int):
    _frozen = False

    def __new__(
        cls,
        value,
        label,
        **kwargs
    ):
        if not isinstance(value, int):
            raise TypeError("Value must be an integer.")
        item = int.__new__(cls, value)
        setUpItem(item, value, label, **kwargs)
        return item


    def __setattr__(self, key, value):
        if self._frozen:
            raise AttributeError("You cannot set attributes on Enums after initial definition")
        super(EnumIntItem, self).__setattr__(key, value)

"""
class EnumStrItem(EnumItem, unicode):
    def __init__(
        self,
        value,
        label,
        **kwargs
    ):
        if not isinstance(value, (str, unicode)):
            raise TypeError("Value must be an string.")
        item = unicode.__new__(cls, value)
        setUpItem(item, value, label, **kwargs)
        return item
"""

class EnumMetaClass(type):
    def __new__(cls, name, bases, d):
        # Set up a dictionary to save all the items in
        d["_items"] = {}

        # For developer convenience, we only raise duplicate value errors at the end,
        # all at once (so they get a complete list every time); this is where those live
        duplicate_errors = []

        # Enforce that all items must be of the same type
        item_type = d.get("item_type", EnumIntItem)

        # Load the default values, if there are any defined on the class
        defaults = d.pop("default_attributes", {})
        d["_attribute_types"] = {
            key: type(value)
            for key, value in six.iteritems(defaults)
        }
        attributes_initialized = False

        # Search functions
        # Create a new class for items of this type
        for key, item in six.iteritems(d):
            if not isinstance(item, EnumItem):
                # This is all just handling EnumItems
                continue

            # Validate that the type of the enum item is correct for this enum
            if not isinstance(item, item_type):
                raise TypeError("Cannot add a {} to an enum of {} items.".format(type(item), item_type))
            
            # validate item uniqueness
            if item.value in d["_items"]:
                duplicate_errors.append("Value {!r} for key {!r} duplicates existing key {!r}".format(
                    item.value,
                    key,
                    d["_items"][item.value].key
                ))
                continue

            # Add default attributes and validate attribute completeness and type-correctness
            for attribute, value in six.iteritems(vars(item)):
                print("Checking attribute {} on {}".format(attribute, item))
                if attribute not in d["_attribute_types"]:
                    if not attributes_initialized:
                        d["_attribute_types"][attribute] = type(value)
                    else:
                        raise AttributeError("Attribute {} of item {} not present on all items.")
                if type(value) is not d["_attribute_types"][attribute]:
                    raise TypeError("Attribute {!r} with value {!r} has the wrong type; has {!r}, expecting {!r}.".format(
                        attribute,
                        value,
                        type(value),
                        d["_attribute_types"][attribute]
                    ))

            attributes_initialized = True

            # Insert all the default attributes of the EnumClass
            item._update_defaults(defaults)

            # Freeze the enum so no further changes can be made
            item._frozen = True
            d["_items"][item.value] = item
            
            # Final check to make sure that all the attributes that were on any enum are on every enum
            for attribute in d["_attribute_types"]:
                if not hasattr(item, attribute):
                    raise AttributeError("Item {} is missing attribute {}".format(item, attribute))

        if duplicate_errors:
            raise AttributeError("Duplicate values detected: {}".format(",".join(duplicate_errors)))

        return type.__new__(cls, name, bases, d)

    def __getattr__(cls_instance, name):
        # type: (str) -> Any
        if name[:3] == "by_":
            return partial(cls_instance.by_attribute, name=name[3:])

class ElevatedEnum(object):
    # do the thing
    __metaclass__ = EnumMetaClass
    item_type = EnumIntItem

    # Define a list of attributes that are enforced as unique and can be searched for using "by_" functions
    unique_attributes = []
    _attribute_types = {}

    @classmethod
    def choices(cls, attribute="label"):
        return [
            (value, getattr(item, attribute))
            for value, item in six.iteritems(cls._items)
        ]

    @classmethod
    def by_value(cls, attribute="label"):
        return [
            (value, getattr(item, attribute))
            for value, item in six.iteritems(cls._items)
        ]
    
    @classmethod
    def to_dict(cls, attributes=None):
        # type: (List) -> List[Dict[unicode, unicode]]

        if attributes is None:
            attributes = [
                attribute
                for attribute in cls._attribute_types
            ]
        return {
            item.value: {
                attribute: getattr(item, attribute)
                for attribute in attributes
            }
            for item in six.itervalues(cls._items)
        }
        
    @classmethod
    def by_attribute(cls, value, name):
        # Confirm the attribute is available
        found_enum = None
        if name not in cls._attribute_types:
            raise AttributeError("Attribute {!r} does not exist on {}".format(name, cls))

        for item in six.itervalues(cls._items):
            if getattr(item, name) == value:
                if found_enum is not None:
                    raise MultipleFound("Found more than one enum with attribute {!r} equal to {!r}".format(
                        name,
                        value
                    ))
                found_enum = item
        if found_enum is None:
            raise NotFound("No enum found with attribute {!r} equal to {!r}".format(name, value))
        return found_enum
