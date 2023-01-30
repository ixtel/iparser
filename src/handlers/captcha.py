from ..config import log


def captcha_check_img(cls):
	_task_id = None
	_answer = None
	_captcha_file = None
	_send_answer = False
	_nocaptcha = False
	__captcha = ''
	
	try:
		for i in range(cls._captcha_repeat + 1):
			_captcha = cls._get_url_img()
			if not _captcha:
				_nocaptcha = True
				break
			log(f'Have captcha url={_captcha} try {i}')
			
			if _captcha != __captcha:
				log(f'Is New captcha url={_captcha}')
				# если адрес капчи изменился
				_answer, _captcha_file, _task_id = cls._get_answer_img(_captcha)
				# получаем ответ, адрес файла каптчи и id задачи на антигейте
			
			if not _answer:
				log(f'Fail answer captcha_file={_captcha_file}, task_id={_task_id}')
				# если нет решения сохраняем в базу файл каптчи
				cls._save_answer_img(_answer, _captcha_file, 0)
				continue
			
			_send_answer = cls._send_answer_img(_answer)
			# отправляем ответ
			
			__captcha = cls._get_url_img()
			
			if _send_answer is None or not __captcha:
				log(f'Maybe send_answer={_send_answer} new_captcha={__captcha}')
				# если нет поля ввода ответа или нет самой каптчи Успех
				_nocaptcha = True
				break
			
			log(f'Steal captcha={__captcha} and answer={_answer}')
			# если все еще в этом цикле значит капча есть.
			if _answer and _send_answer and _task_id and _captcha != __captcha:
				# если есть ответ и он отправлен и есть id задачи и урл каптчи другой
				log(f'Save answer to db answer={_answer}, captcha_file={_captcha_file}')
				cls._save_answer_img(_answer, _captcha_file, -1)
				# сохраняем ошибочный ответ, файл каптчи и статуст в базу
				if cls.anticapcha_options['report']:
					log(f'Send Report for answer={_answer}, task_id={_task_id}')
					# если отправлять репорты. отправляем
					cls._send_report_img(_task_id)
		
		if _answer and _captcha_file:
			# если есть ответ и файл каптчи
			if _nocaptcha:
				# если распознан
				log(f'Good recognized answer={_answer}, captcha_file={_captcha_file}')
				cls._save_answer_img(_answer, _captcha_file, 1)
			else:
				log(f'Fail recognized answer={_answer}, captcha_file={_captcha_file}')
				# если не распознан
				cls._save_answer_img(_answer, _captcha_file, 0)
		
		log('Captcha isClean', _nocaptcha, '_task_id', _task_id, '_answer', _answer, '_captcha_file', _captcha_file, '_send_answer', _send_answer)
		return _nocaptcha
	except Exception as ex:
		log('Exception', ex, level='warning')
		raise ex
