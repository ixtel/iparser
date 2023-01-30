class CustomBaseException(Exception):
	def __init__(self, salary, message="Exception"):
		self.salary = salary
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f'{self.message} -> {self.salary}'


class ElementIsNone(CustomBaseException):
	def __init__(self, salary, message="Element is None"):
		super().__init__(salary, message)


class SelectorIsNone(CustomBaseException):
	def __init__(self, salary, message="Element is None"):
		super().__init__(salary, message)
