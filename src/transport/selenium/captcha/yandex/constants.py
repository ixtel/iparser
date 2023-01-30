class CaptchaRoutesYandex(object):
	SMART = [
		'div.CheckboxCaptcha-Checkbox',
		'input.CheckboxCaptcha-Button',
	]
	
	SMART_BAN = [
	
	]
	
	IMG = [
		'img.captcha__image',
		'img.form__captcha',
		'img.AdvancedCaptcha-Image',
		'img.captcha__captcha__text',
	]
	
	IMG_ERROR = [
		'.captcha-wrapper .field__error'
	]
	
	IMG_HEAD = [
	]
	
	INPUT = [
		'form input#rep',
		'form input#captcha',
		'.AdvancedCaptcha-FormField input.Textinput-Control',
		'#passp-field-captcha_answer',
		'input[name="captcha_answer"]',
		'input#answer',
		'input[name="answer"]',
		'input',
	]
	
	SEND = [
		'form button.form__submit',
		'*.form__submit button',
		'button.Button2_view_action',
		'button[data-testid="submit"]',
		'button[type="submit"]',
		'button',
	]
	
	RELOAD = [
		'*.captcha__reload',
		'div.AdvancedCaptcha-FormActions button.Button2_view_clear',
		'button[data-testid="refresh"]',
	]
