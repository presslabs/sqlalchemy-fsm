import collections
from functools import wraps
from sqlalchemy import types as SAtypes

class FSMMeta(object):
  def __init__(self):
    self.transitions = collections.defaultdict()
    self.conditions = collections.defaultdict()

  @staticmethod
  def _get_state_field(instance):
    fsm_fields = [c for c in instance.__table__.columns \
                  if isinstance(c.type, FSMField)]

    if len(fsm_fields) == 0:
      raise TypeError('No FSMField found in model')

    if len(fsm_fields) > 1:
      raise TypeError('More than one FSMField found in model')
    else:
      return fsm_fields[0]

  @staticmethod
  def current_state(instance):
    field_name = FSMMeta._get_state_field(instance).name
    return getattr(instance, field_name)

  def has_transition(self, instance):
    return FSMMeta.current_state(instance) in self.transitions or\
        '*' in self.transitions

  def conditions_met(self, instance, *args, **kwargs):
    current_state = FSMMeta.current_state(instance)
    next_state = current_state in self.transitions and\
        self.transitions[current_state] or self.transitions['*']
    return all(map(lambda f: f(instance, *args, **kwargs),
               self.conditions[next_state]))

  def to_next_state(self, instance):
    field_name = FSMMeta._get_state_field(instance).name
    current_state = getattr(instance, field_name)
    next_state = None

    try:
      next_state = self.transitions[current_state]
    except KeyError:
      next_state = self.transitions['*']

    setattr(instance, field_name, next_state)

def can_proceed(bound_method, *args, **kwargs):
  if not hasattr(bound_method, '_sa_fsm'):
    raise NotImplementedError('%s method is not transition' %\
        bound_method.im_func.__name__)

  meta = bound_method._sa_fsm
  return meta.has_transition(bound_method.im_self) and\
      meta.conditions_met(bound_method.im_self, *args, **kwargs)

class FSMField(SAtypes.String):
  pass
