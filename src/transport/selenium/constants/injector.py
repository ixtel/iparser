JS_CMD = {
	# размер рабочее пространство где отображается сайт
	# return {width: int, height: int}
	# 'workplace': 'return {"width":window.innerWidth,"height":window.innerHeight}',
	'workplace': 'return get_workplace_size();',
	
	# разрешение экрана(размер монитора)
	# return {width: int, height: int}
	# 'resolute': 'return {"width":window.innerWidth,"height":window.innerHeight}',
	'resolute': 'return get_resolute();',
	
	# размер окна браузера
	# return {width: int, height: int}
	# 'window_size': 'return {"width":window.outerWidth,"height":window.outerHeight}',
	'window_size': 'return get_window_size();',
	
	# высота страницы сайта
	# return int
	# 'body_height': 'return Math.max(document.body.scrollHeight, document.body.offsetHeight,document.body.clientHeight)',
	'body_height': 'return get_current_body_height();',
	
	# ширина страницы сайта
	# return int
	# 'body_width': 'return Math.max(document.body.scrollWidth, document.body.offsetWidth,document.body.clientWidth)',
	'body_width': 'return get_current_body_width();',
	
	# смешение рабочего окна от верха страницы
	# return int
	# 'top': 'return (window.pageYOffset || document.body.scrollTop) - (document.body.clientTop || 0)',
	'top': 'return get_current_top_position();',
	
	# смешение рабочего окна от левого края страницы
	# return int
	# 'left': 'return (window.pageXOffset || document.body.scrollLeft) - (document.body.clientLeft || 0)',
	'left': 'return get_current_left_position();',
	
	# высота страницы ниже текущего окна
	# return int
	'bottom': 'return get_current_bottom_position();',
	
	# длинна страницы правее текущего окна
	# return int
	'right': 'return get_current_right_position();',
	
	# y координата нижнего края текущего окна
	# return int
	'downline': 'return get_current_downline();',
	
	# x координата правого края текущего окна
	# return int
	'rightline': 'return get_current_rightline();',
	
	# координтаы видимого пространства страницы
	# return [[left, rightline], [top, downline]]
	'current_workplace': 'return get_current_workplace();',
	
	'scroll': 'window.scrollTo({0}, {1})',
	
	'stop_load': 'window.stop',
	
	'element_set_value': 'arguments[0].value = "{}";',
	
	'element_border': 'arguments[0].style.border = "1px solid #{}";',
	
	'element_click_jsxpath': '''get_elm_by_xpath('{0}', '{1}').click();''',
	'element_click_jscss': '''element_click_jscss('{0}', '{1}');''',
	'element_click_js': 'element_click_js(arguments[0]);',
	'element_position_static': '''element_set_position_static('{0}');''',
	
	'element_style': '''arguments[0].style.{0}='{1}';''',
	
	'element_top': '''arguments[0].style.setProperty('z-index', '99999999');''',
	
	# Удалить содержимое элемента
	'element_clean': 'document.querySelector("{0}").outerHTML = "";',
	
	'link_blanc_off': '''arguments[0].setAttribute('target', '');''',
	
	'heatmap_set': '''
		document.body.innerHTML += ''+
			'<div id="heatmapContainerWrapper" style="width: 100%;height: {0}px; position: absolute; top:0;left:0;">'
				'<div id="heatmapContainer" style="width: 100%;height: {0}px;top:0;left:0;">'+
				'</div>'+
			'</div>';
		var heatmap_scr = document.createElement("script");
		heatmap_scr.innerHTML={1}{2};
		document.body.appendChild(heatmap_scr);
		''',
	'mouse_trail_off': '''
			var div_trail = document.getElementsByClassName('trail');
			for(var i=div_trail.length-1; i>=0; --i){
				div_trail[i].outerHTML=''
			};''',
	
	'js_helper_set': '''
			var js_helper_container = document.createElement("div");
			js_helper_container.id = 'js_helper_coordinator';
			js_helper_container.style.cssText = 'display:none';

			var js_helper_scr = document.createElement("script");
			js_helper_scr.type = 'text/javascript';
			js_helper_scr.innerHTML=`{0}`;

			js_helper_container.appendChild(js_helper_scr);
			document.body.appendChild(js_helper_container);
			''',
	
	'xpather_set': '''
			var xpather_container = document.createElement("div");
			xpather_container.id = 'selectorxpathcss';
			xpather_container.style.cssText = 'display:none';

			var xpather_scr = document.createElement("script");
			xpather_scr.type = 'text/javascript';
			xpather_scr.innerHTML=`{0}`;

			xpather_container.appendChild(xpather_scr);
			document.body.appendChild(xpather_container);
			''',
	
	'xpath_on_coordinates': '''return createXPathFromElement(element_on_coordinates({0},{1}))''',
	'css_on_coordinates': '''return createCssFromElement(element_on_coordinates({0},{1}))''',
	'xpath_on_element': '''return createXPathFromElement(arguments[0])''',
	'css_on_element': '''return createCssFromElement(arguments[0])''',
	
	'element_on_coordinates': '''return element_on_coordinates({0},{1})''',
	'cursor_position': '''
		let cursorForm = document.createElement("div")
		cursorForm.innerHTML = ''+
		'<form name="cursorShowCoordinates" style="display:none; position:fixed; left:0; top:0; z-index:9999;">'+
			'<input type="text" name="MouseX" id="MouseX" value="0">'+
			'<input type="text" name="MouseY" id="MouseY" value="0">'+
		'</form>';
		document.body.appendChild(cursorForm)
		function getMouseXY(e) {{
			document.cursorShowCoordinates.MouseX.value = e.pageX;
			document.cursorShowCoordinates.MouseY.value = e.pageY;
			return
		}}
		document.onmousemove = getMouseXY
		''',
}
