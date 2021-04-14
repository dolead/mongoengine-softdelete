from mongoengine.signals import _signals

pre_soft_delete = _signals.signal('pre_soft_delete')
post_soft_delete = _signals.signal('post_soft_delete')
pre_soft_undelete = _signals.signal('pre_soft_undelete')
post_soft_undelete = _signals.signal('post_soft_undelete')
