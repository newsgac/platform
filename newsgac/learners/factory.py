from . import learners


def create_learner(tag, with_defaults=True, **kwargs):
    for learner in learners:
        if learner.tag == tag:
            if with_defaults:
                return learner.new(**kwargs)
            else:
                return learner(**kwargs)
    raise ValueError('No learner with tag "%s"' % tag)
