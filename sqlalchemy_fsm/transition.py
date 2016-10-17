import collections
from functools import wraps

from sqlalchemy_fsm import FSMMeta
from sqlalchemy_fsm.exceptions import InvalidTransition

def transition(source = '*', target = None, conditions = ()):
  def inner_transition(func):

    def isstring(candidate):
      return isinstance(candidate, (''.__class__, u''.__class__))

    if not hasattr(func, '_sa_fsm'):
      setattr(func, '_sa_fsm', FSMMeta())
    if isinstance(source, collections.Sequence) and not isstring(source):
      for state in source:
        func._sa_fsm.transitions[state] = target
    else:
      func._sa_fsm.transitions[source] = target

    func._sa_fsm.conditions[target] = conditions

    @wraps(func)
    def _change_state(instance, *args, **kwargs):
      meta = func._sa_fsm

      if not meta.has_transition(instance):
        raise InvalidTransition('Cant switch from %s using method %s'\
                            % (FSMMeta.current_state(instance), func.__name__))

      for condition in conditions:
        if not condition(instance, *args, **kwargs): return False

      func(instance, *args, **kwargs)
      meta.to_next_state(instance)

    return _change_state

  if not target:
    raise ValueError('Result state not specified')

  return inner_transition
