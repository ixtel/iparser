from typing import Union

from itools.dataminer.parser import xpath_cls_repl
from grab.document import Document
from ...config import log


class Selector:
	def __init__(self, *args, **kwargs):
		pass
	
	@staticmethod
	def _select(obj: Document, selector: Union[str, list]):
		try:
			elm = obj.select(xpath_cls_repl(selector))
			return elm
		except Exception as _ex:
			log(f'Exception, {_ex}', level='warning')
			return None
	
	def select(self, obj: Document, selector: Union[str, list], attr=None, attr_name=None, one=False):
		if not isinstance(selector, list):
			selector = [selector]
		for p in selector:
			elm = self._select(obj, p)
			if elm is not None:
				try:
					if one:
						elm = elm.one()
					if attr is not None:
						try:
							_r = getattr(elm, attr)()
						except Exception as ex:
							log(f'Exception', ex, level='warning')
							_r = None
					elif attr_name is not None:
						try:
							_r = elm.attr(attr_name)
						except Exception as ex:
							log(f'Exception', ex, level='warning')
							_r = None
					else:
						_r = elm
					if _r:
						return _r
					continue
				except Exception as _ex:
					log(f'Exception, {_ex}', level='warning')
					pass
		return None
	
	def select_one(self, obj: Document, selector: Union[str, list], attr=None, attr_name=None):
		return self.select(obj=obj, selector=selector, attr=attr, attr_name=attr_name, one=True)
