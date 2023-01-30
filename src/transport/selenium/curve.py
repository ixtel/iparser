import math
import statistics
from random import randint, choice, uniform

from itools.geometro.curves import bezier_curve
from shapely.geometry import LineString

from .config import log

__all__ = ('MouseCurve',)


def frange(start=0.1, stop=1, step=0.1, reverse=False):
	if reverse:
		while start < stop:
			yield stop
			stop -= step
	else:
		while start < stop:
			yield start
			start += step


class MouseCurve:
	def __init__(self):
		self._current_workplace = [[0, 0], [0, 0]]
	
	def track_from_2point(self, start, end, current_workplace):
		self._current_workplace = current_workplace
		points = self._vector_points(start, end)
		# TODO если мышь сдвинулась до проверки, все закцикливается, надо каждый раз при проверке чекать начальную точку и вычислять кривую
		points_bz = self._points_bezier(points)
		points_bz_sp = self._track_speeder(points_bz)
		track = self._vector_steps_by_pooint(points_bz_sp)
		return track
	
	def teleport_from_2point(self, start, end):
		points = self._vector_points(start, end)
		points = [points[0], points[-1]]
		track = self._vector_steps_by_pooint(points)
		return track
	
	@staticmethod
	def _vector_stop(length, vector_to_end):
		log(f'length={length}, vector_to_end={vector_to_end}', level='debug')
		# TODO: рефакторинг vector_stop
		return True
	
	@staticmethod
	def _vector(start, end):
		"""
		:param start: координата
		:param end: координата
		:return: вектор объект
		"""
		coordinates = [(int(start['x']), int(start['y'])), (int(end['x']), int(end['y']))]
		line = LineString(coordinates)
		return line, int(line.length)
	
	@staticmethod
	def _vector_end_point(start, end):
		"""
		:param start: координата
		:param end: координата
		:return: dict = {key: int(end[key]) - int(start.get(key, 0)) for key in end.keys()}
		"""
		return {
			'x': int(end['x']) - int(start.get('x', 0)),
			'y': int(end['y']) - int(start.get('y', 0)),
		}
	
	@staticmethod
	def _vector_point(length, line, delta=1):
		delta = delta if delta else length
		fragment_lenght = randint(1, min(delta, length))
		step = line.interpolate(fragment_lenght, normalized=False).coords[0]
		next_point = {'x': math.ceil(step[0]), 'y': math.ceil(step[1])}
		return next_point, fragment_lenght
	
	def _vector_points(self, start, end, delta=0):
		"""
		разбивает вектор из начала в конец на более мелкие кусочки
		:param start: начальная точка
		:param end: конечная точка
		:param delta: длинна вектора между промежуточными точками
		:return: список координат по которым надо двигатся
		"""
		line, length = self._vector(start, end)
		delta = delta if delta else length
		points = []
		while length > 1:
			points.append(dict(start))
			next_point, fragment_lenght = self._vector_point(max(length, 1), line, delta)
			vector_to_end = self._vector_end_point(start, next_point)
			if self._vector_stop(fragment_lenght, vector_to_end):
				start = next_point
				line, length = self._vector(start, end)
			else:
				length = 0
		points.append(dict(end))
		return points
	
	def _vector_steps_by_pooint(self, points):
		vectors = []
		for i, p in enumerate(points):
			if i < len(points) - 1:
				vector_to_end = self._vector_end_point(p, points[i + 1])
				vectors.append(vector_to_end)
		return vectors
	
	@staticmethod
	def _average(points: list):
		# сглаживание по двум точкам
		my = []
		for i, v in enumerate(points):
			if i == 0:
				v2 = 0
			elif i == (len(points) - 1):
				v2 = 0
			else:
				v2 = points[i - 1]
			y = (v + v2) / 2
			my.append(y)
		return my
	
	@staticmethod
	def __dys(dx, param: tuple):
		dy = []
		lens = len(dx)
		(k1, k2, k3, k4) = param
		for x in dx:
			y = (lens * k1 - x) / ((lens * k2) + x * k3) * x / k4
			y = 1 / y if y > 0 else 0
			dy.append(y)
		return dy
	
	def _speed_curve(self, points):
		dx = list(range(1, len(points) + 1))
		param = (1, 2, 1, 5)
		dy = self.__dys(dx, param)
		speeds = self._average(dy)
		return speeds
	
	@staticmethod
	def _speeder(points, speeds, delta=0.005):
		t = 0
		speeder = []
		# TODO: выкидывает часть хвоста из списка точек
		av = statistics.mean(speeds) * randint(1, 15)
		delta = delta if delta else av
		
		speeder.append(points[0])
		for i, r in enumerate(points):
			t += speeds[i]
			if t >= delta or t == 0:
				speeder.append(r)
				t = speeds[i]
			else:
				pass
		speeder.append(points[-1])
		return speeder
	
	@staticmethod
	def _vector_plus(start, end):
		return {key: int(end[key]) + int(start.get(key, 0)) for key in end.keys()}
	
	def _points_bezier_check_worplace(self, points):
		try:
			left_point = min(map(lambda i: i['x'], points))
			right_point = max(map(lambda i: i['x'], points))
			top_point = min(map(lambda i: i['y'], points))
			bottom_point = max(map(lambda i: i['y'], points))
			((left, right), (top, bottom)) = self._current_workplace
		except Exception as ex:
			log(f'Exception points={points}', ex, level='warning')
			raise ex
		return left < left_point and right > right_point and top < top_point and bottom > bottom_point
	
	def _points_bezier(self, points):
		"""
		преобразование прямого вектора в кривую
		:param points: список точек вектора
		:return:
		"""
		try:
			divisor = 1.0
			for i in frange(0.1, 1, 0.1, reverse=True):
				try:
					result_points = self._points_bezier_generate(points, divisor=divisor * i)
					if self._points_bezier_check_worplace(result_points):
						return result_points
				except Exception as ex:
					log('Exception points_bezier', ex, level='critical')
					raise ex
			log('Warning not gen points', level='warning')
			return points
		except Exception as ex:
			log(f'Exception', ex, level='critical')
			return points
	
	def _points_bezier_generate(self, points, divisor: float = 1.0):
		bz_d, xd, yd = self._bizier_gen_point(points, divisor=divisor)
		num = len(points) * 2
		try:
			bz_points, bxd, byd = bezier_curve(bz_d, num)
		except Exception as ex:
			log(f'Exception', ex, level='warning')
			raise ex
		return bz_points
	
	def _track_speeder(self, points, delta=False):
		speeds = self._speed_curve(points)
		speeder_points = self._speeder(points, speeds, delta=delta)
		return speeder_points
	
	def _bizier_gen_point(self, points, divisor: float = 1.0):
		# TODO переписать полностью функции кривых. убрать в геометро.
		try:
			start, end = points[0], points[-1]
			# случайная точка в массиве
			p = choice(points)
			# получаем вектор и длинну из начала в конец
			vector, lenght = self._vector(start, end)
			# длинна отклонения для построения кривизны
			# dt = lenght / choice([uniform(4, 8), uniform(12, 30)])
			dt = lenght * uniform(0.01, 0.5 * divisor)
			# угол с какой стороны вектора будет кривизна
			angle = choice([90, 180])
			
			need_vect = {
				'x': dt * math.cos(angle),
				'y': dt * math.sin(angle)
			}
			need_point = self._vector_plus(p, need_vect)
			bz_points = [start, need_point, end]
			xd = []
			yd = []
			for b in bz_points:
				xd.append(b['x'])
				yd.append(b['y'])
		except Exception as ex:
			log(f'Exception divisor={divisor}, points=points{points}', ex, level='warning')
			raise ex
		return bz_points, xd, yd
