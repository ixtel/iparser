from random import randint, uniform, shuffle


def random_chunk_distance(a=0, b=10):
	delta = float(b) - float(a)
	result = []
	count = randint(1, 4)
	i = 0
	while delta > a or i == count:
		_distance = uniform(0, delta)
		delta -= _distance
		result.append(_distance)
	if delta > 0:
		result.append(delta)
	shuffle(result)
	return result


def sizer(d):
	_s = {
		'x': d['width'],
		'y': d['height']
	}
	return _s


def clean_url(url):
	url = url.replace('http://', '')
	url = url.replace('https://', '')
	if url.endswith('/'):
		url = url[:-1]
	return url
