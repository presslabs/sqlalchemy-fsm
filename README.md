Finite state machine field for sqlalchemy (based on django-fsm)
==============================================================

sqlalchemy-fsm adds declarative states management for sqlalchemy models.
Instead of adding some state field to a model, and manage its
values by hand, you could use FSMState field and mark model methods
with the `transition` decorator. Your method will contain the side-effects
of the state change.

The decorator also takes a list of conditions, all of which must be met
before a transition is allowed.

Usage
-----

Add FSMState field to you model

    from sqlalchemy_fsm import FSMField, transition

    class BlogPost(db.Model):
        state = db.Column(FSMField, nullable = False)


Use the `transition` decorator to annotate model methods

    @transition(source='new', target='published')
    def publish(self):
        """
        This function may contain side-effects, 
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """

`source` parameter accepts a list of states, or an individual state.
You can use `*` for source, to allow switching to `target` from any state.

If calling publish() succeeds without raising an exception, the state field
will be changed, but not written to the database.

    from sqlalchemy_fsm import can_proceed

    def publish_view(request, post_id):
        post = get_object__or_404(BlogPost, pk=post_id)
        if not can_proceed(post.publish):
             raise Http404;

        post.publish()
        post.save()
        return redirect('/')


If your given function requires arguments to validate, you need to include them
when calling can_proceed as well as including them when you call the function
normally. Say publish() required a date for some reason:

    if not can_proceed(post.publish, the_date):
        raise Http404
    else:
        post.publish(the_date)

If you require some conditions to be met before changing state, use the
`conditions` argument to `transition`. `conditions` must be a list of functions
that take one argument, the model instance.  The function must return either
`True` or `False` or a value that evaluates to `True` or `False`. If all
functions return `True`, all conditions are considered to be met and transition
is allowed to happen. If one of the functions return `False`, the transition
will not happen. These functions should not have any side effects.

You can use ordinary functions

    def can_publish(instance):
        # No publishing after 17 hours
        if datetime.datetime.now().hour > 17:
           return False
        return True

Or model methods

    def can_destroy(self):
        return self.is_under_investigation()

Use the conditions like this:

    @transition(source='new', target='published', conditions=[can_publish])
    def publish(self):
        """
        Side effects galore
        """

    @transition(source='*', target='destroyed', conditions=[can_destroy])
    def destroy(self):
        """
        Side effects galore
        """


How does sqlalchemy-fsm diverge from django-fsm?
------------------------------------------------

* Can't commit data from within transition-decorated functions

* No pre/post signals

* Does support arguments to conditions functions
