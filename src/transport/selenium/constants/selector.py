BLOCKS_CLOSE = [
	# первый элемент селектор который кликать, второй селектор если он в iframe
	('.modal__close', ''),
	('.distr-popup__close', ''),
]

BLOCKS_REMOVE = [
	'.jsrp',
	'iframe[src*="youtube"]',
	'div[data-related-above-place="top"]',
	'nav.navigation_type_horizontal',
	'.main__distr-splashscreen',
	'.distr-splashscreen',
	'.modal',
	# TODO: iframe youtube удалять все а не только первый. перенести в отдельную функцию cmd.instance -> JS:: foreach list

]

SEARCH = {
	'yandex': {
		'search_input': [
			'form[role="search"] input#text',
			'form[role="search"] input[name="text"]',
		],
		'region_input': [
			'input[name="lr"]',
		],
		'search_button': [
			'form[role="search"] button[type="submit"]',
		],
		'search_next': [
			'div.pager a.pager__item:last-of-type',
			'.pager a:last-of-type',
		],
		'searchengines_list': [
			'div.searchengines__list a',
		],
		'search_result_list': [
			'.serp-list .serp-item',
		],
		'search_result_link': [
			'a',
		],
		'block_excepte': [
			'div.organic__subtitle',
			'div.serp-url'
		],
		'block_flow': [
			'.serp-header__wrapper',
			'.head-stripe',
			'.head-stripe__table',
			'.footer-stripe',
			'.navigation_more-type_slide',
			'.navigation_type_horizontal',
		],
	},
	'google': {
		'search_input': ['input[name="q"]'],
		'search_button': [
			'input[name="btnK"]',
			'button[type="submit"]',
		],
		'search_next': [
			'a#pnnext',
			'div#foot > table#nav a.fl:last-of-type',
			'div[role="navigation"] td a:last-of-type',
			'footer a:last-of-type',
		],
		'search_result_list': [
			'div.g',
			'div#main > div > div > div',
		],
		'search_result_link': [
			'a',
		],
	},
}

SEARCH_STOP_URLS = [
	'aliexpress',
	'google',
	'yandex',
	'youtube',
]

SEARCH_STOP_WORDS = [
	'реклама',
	'яндекс',
]
