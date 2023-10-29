### Elevated Enum

## Primary Requirements:

# Imported from Python Enum Class
- [ ] the TYPE of a member is the ElevatedEnum to which it belongs
- 

# Imported from common.Enum:
- [ ] Supports either Integer or String values
- [X] When referenced in isolation, the Value is returned in a way that it is a direct substitite for the Value Type
- 

# Relative to Django Support
- [X] Can easily be defined as choices= for a Django Model

# Based on in-use experience:
- [X] When defining a class, raise an error as early as possible for duplicate Values or Keys
- [X] Enforce that you cannot add new properties to an Enum outside of its initial definition
- [ ] Add easy entrypoints for testing uniqueness
- [ ] Add ability to cache existing values and easily detect changes
- [ ] Easy extension of existing classes _without_ subclassing - so the inheriting class has members with the same values, but the new members are not the same as the old members
- [X] Easily define default attributes
- [X] Easily list out Enum values and _specified_ attributes, similar to Django .values() behavior
- [ ] Easily filter Enum instances by attribute, similar to Django .filter() behavior
- [X] Easily list out the definition of an enum


## Deliberate Departures from Existing Practice:

# From Python Enum Class:
- The @unique decorator is not used, because in this instance it is assumed to always apply
- A form of inheritance is allowed, for occasions where one EnrichedEnum is a superset of another