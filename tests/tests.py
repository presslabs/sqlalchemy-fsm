import unittest, sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_fsm import FSMField, transition, can_proceed
from sqlalchemy_fsm.exceptions import InvalidTransition

engine = sqlalchemy.create_engine('sqlite:///:memory:', echo = True)
session = sessionmaker(bind = engine)
Base = declarative_base()

class BlogPost(Base):
  __tablename__ = 'blogpost'

  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
  state = sqlalchemy.Column(FSMField)

  def __init__(self, *args, **kwargs):
    self.state = 'new'
    super(BlogPost, self).__init__(*args, **kwargs)

  @transition(source='new', target='published')
  def publish(self):
    pass

  @transition(source='published', target='hidden')
  def hide(self):
    pass

  @transition(source='new', target='removed')
  def remove(self):
    raise Exception('No rights to delete %s' % self)

  @transition(source=['published','hidden'], target='stolen')
  def steal(self):
    pass

  @transition(source='*', target='moderated')
  def moderate(self):
    pass

class FSMFieldTest(unittest.TestCase):
  def setUp(self):
    self.model = BlogPost()

  def test_initial_state_instatiated(self):
    self.assertEqual(self.model.state, 'new')

  def test_known_transition_should_succeed(self):
    self.assertTrue(can_proceed(self.model.publish))
    self.model.publish()
    self.assertEqual(self.model.state, 'published')

    self.assertTrue(can_proceed(self.model.hide))
    self.model.hide()
    self.assertEqual(self.model.state, 'hidden')

  def test_unknow_transition_fails(self):
    self.assertFalse(can_proceed(self.model.hide))
    self.assertRaises(InvalidTransition, self.model.hide)

  def test_state_non_changed_after_fail(self):
    self.assertRaises(Exception, self.model.remove)
    self.assertTrue(can_proceed(self.model.remove))
    self.assertEqual(self.model.state, 'new')

  def test_mutiple_source_support_path_1_works(self):
    self.model.publish()
    self.model.steal()
    self.assertEqual(self.model.state, 'stolen')

  def test_mutiple_source_support_path_2_works(self):
    self.model.publish()
    self.model.hide()
    self.model.steal()
    self.assertEqual(self.model.state, 'stolen')

  def test_star_shortcut_succeed(self):
    self.assertTrue(can_proceed(self.model.moderate))
    self.model.moderate()
    self.assertEqual(self.model.state, 'moderated')


class InvalidModel(Base):
  __tablename__ = 'invalidmodel'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
  state = sqlalchemy.Column(FSMField)
  action = sqlalchemy.Column(FSMField)

  def __init__(self, *args, **kwargs):
    self.state = 'new'
    self.action = 'no'
    super(InvalidModel, self).__init__(*args, **kwargs)

  @transition(source='new', target='no')
  def validate(self):
    pass

class InvalidModelTest(unittest.TestCase):
  def test_two_fsmfields_in_one_model_not_allowed(self):
    model = InvalidModel()
    self.assertRaises(TypeError, model.validate)


class Document(Base):
  __tablename__ = 'document'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
  status = sqlalchemy.Column(FSMField)

  def __init__(self, *args, **kwargs):
    self.status = 'new'
    super(Document, self).__init__(*args, **kwargs)

  @transition(source='new', target='published')
  def publish(self):
    pass


class DocumentTest(unittest.TestCase):
  def test_any_state_field_name_allowed(self):
    model = Document()
    model.publish()
    self.assertEqual(model.status, 'published')

def condition_func(instance):
  return True


class BlogPostWithConditions(Base):
  __tablename__ = 'BlogPostWithConditions'
  id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
  state = sqlalchemy.Column(FSMField)

  def __init__(self, *args, **kwargs):
    self.state = 'new'
    super(BlogPostWithConditions, self).__init__(*args, **kwargs)

  def model_condition(self):
    return True

  def unmet_condition(self):
    return False

  @transition(source='new', target='published', conditions=[condition_func, model_condition])
  def publish(self):
    pass

  @transition(source='published', target='destroyed', conditions=[condition_func, unmet_condition])
  def destroy(self):
    pass


class ConditionalTest(unittest.TestCase):
  def setUp(self):
    self.model = BlogPostWithConditions()

  def test_initial_staet(self):
    self.assertEqual(self.model.state, 'new')

  def test_known_transition_should_succeed(self):
    self.assertTrue(can_proceed(self.model.publish))
    self.model.publish()
    self.assertEqual(self.model.state, 'published')

  def test_unmet_condition(self):
    self.model.publish()
    self.assertEqual(self.model.state, 'published')
    self.assertFalse(can_proceed(self.model.destroy))
    self.model.destroy()
    self.assertEqual(self.model.state, 'published')

if __name__ == '__main__':
  unittest.main()
