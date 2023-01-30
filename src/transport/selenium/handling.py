from .actions import Actions

__all__ = ('Handling',)


class Handling(Actions):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
