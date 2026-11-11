"""Effects package initialization.

Defines the exported submodules and package effect helpers.

Complexity:
  Input size: N = number of items in the effects collection.
  Time Complexity: O(N) linear time to iterate and produce the normalized list.
  Space Complexity: O(N) auxiliary space for the returned list.
"""

__all__ = ['echo']

AVAILABLE_EFFECTS = ['echo']


def list_effects(effects=None):
    """Return list of effects from given collection or defaults.

    Precondition line: 17
    Input: effects (list of str or None)
    Output: list of str
    Complexity: O(N) where N is len(effects).
    """
    if effects is None:
        return list(AVAILABLE_EFFECTS)
    return [effect for effect in effects]
