"""Echo effect."""

DEFAULT_ACTION = 'Do'
DEFAULT_EFFECT = 'echo effect'


def format_effect_message(action=DEFAULT_ACTION, effect=DEFAULT_EFFECT):
    """Format an effect message from an action verb and effect descriptor."""
    return f"{action} {effect}"


def echo_function(action=DEFAULT_ACTION, effect=DEFAULT_EFFECT):
    """Echo function mock.

    Refactored to cleanly separate action verb formatting from the effect descriptor.
    Preserves default signature and return contract:
      echo_function() -> 'Do echo effect'
    """
    return format_effect_message(action=action, effect=effect)

