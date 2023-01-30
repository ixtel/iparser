function element_on_coordinates(x, y) {
    return document.elementFromPoint(x - window.pageXOffset, y - window.pageYOffset)
}

function createXPathFromElement(elm) {
    let allNodes = document.getElementsByTagName('*')
    // let segs = []
    // noinspection ES6ConvertVarToLetConst
    for (var segs = []; elm && elm.nodeType === 1; elm = elm.parentNode) {
        if (elm.hasAttribute('id')) {
            let uniqueIdCount = 0
            // noinspection ES6ConvertVarToLetConst
            for (var n = 0; n < allNodes.length; n++) {
                if (allNodes[n].hasAttribute('id') && allNodes[n].id === elm.id) uniqueIdCount++
                if (uniqueIdCount > 1) break
            }
            if (uniqueIdCount === 1) {
                segs.unshift('id("' + elm.getAttribute('id') + '")')
                return segs.join('/')
            } else {
                segs.unshift(elm.localName.toLowerCase() + '[@id="' + elm.getAttribute('id') + '"]')
            }
        } else {
            // noinspection ES6ConvertVarToLetConst
            for (var i = 1, sib = elm.previousSibling; sib; sib = sib.previousSibling) {
                if (sib.localName === elm.localName) i++
            }
            segs.unshift(elm.localName.toLowerCase() + '[' + i + ']')
        }
    }
    return segs.length ? '/' + segs.join('/') : null
}

function _get_xpath_result_from_contextNode(xpathStr, contextNode = null, resultType = 'single') {
    let context = document
    if (typeof contextNode == "object") {
        context = contextNode
    }
    let resultTypeNum
    switch (resultType) {
        case "set":
            resultTypeNum = 7
            break
        case "single":
            resultTypeNum = 9
            break
        case "string":
            resultTypeNum = 2
            xpathStr = "string(" + xpathStr + ")"
            break
        default:
            return false
    }
    let nodesFound = context.evaluate(xpathStr, context, null, resultTypeNum, null)
    try {
        switch (resultType) {
            case "set":
                let result = []
                // noinspection ES6ConvertVarToLetConst
                for (var i = 0; i < nodesFound.snapshotLength; i++) {
                    result.push(nodesFound.snapshotItem(i))
                }
                return result
            case "single":
                return nodesFound.singleNodeValue
            case "string":
                resultType = 2
                return nodesFound.stringValue
        }
        return nodesFound
    } catch (e) {
        return false
    }
}

function get_elm_by_xpath(xpathStr, iframeXpath = false, resultType = 'single') {
    let context = document
    if (iframeXpath) {
        let iframe = (document.evaluate(iframeXpath, document, null, 9, null)).singleNodeValue
        if (iframe === null) {
            context = document
        } else {
            context = iframe.contentDocument || iframe.contentWindow.document
        }
    }
    return _get_xpath_result_from_contextNode(xpathStr, context, resultType)
}

// function get_xpath_result_list(xpathStr){return _get_xpath_result_from_contextNode(xpathStr, document, 'set')}


/*
function createCssFromElement(el){
	let path = [], parent
	while (parent = el.parentNode) {
		let tag = el.tagName, siblings
		path.unshift(
			el.id ? '#' + el.id : (
				siblings = parent.children,
				[].filter.call(siblings, sibling => sibling.tagName === tag).length === 1 ? tag : tag + ':nth-child(' + (1+[].indexOf.call(siblings, el)) + ')'
			)
		)
		el = parent
	}
	return path.join(' > ').toLowerCase()
}
*/
function createCssFromElement(el) {
    let names = []
    while (el.parentNode) {
        if (el.id) {
            names.unshift('#' + el.id)
            break
        } else {
            if (el === el.ownerDocument.documentElement || el === el.ownerDocument.body) {
                names.unshift(el.tagName)
            } else {
                // noinspection ES6ConvertVarToLetConst
                for (var c = 1, e = el; e.previousElementSibling; e = e.previousElementSibling, c++) {
                }
                names.unshift(el.tagName + ':nth-child(' + c + ')')
            }
            el = el.parentNode
        }
    }
    return names.join(' > ')
}

function _get_css_result_from_contextNode(cssStr, contextNode = null) {
    let context = document
    if (typeof contextNode == "object") {
        context = contextNode
    }
    try {
        return context.querySelector(cssStr)
    } catch (e) {
        return null
    }
}

function get_elm_by_css(cssStr, iframeCss = false) {
    let context = document
    if (iframeCss) {
        try {
            let iframe = document.querySelector(iframeCss)
            if (iframe === null) {
                context = document
            } else {
                context = iframe.contentDocument || iframe.contentWindow.document
            }
        } catch (e) {
            context = document
        }
    }
    return _get_css_result_from_contextNode(cssStr, context)
}

function element_click_js(element) {
    try {
        element.click()
    } catch (e) {
        return null
    }
}

function element_click_jscss(cssStr, iframeCss = false) {
    try {
        get_elm_by_css(cssStr, iframeCss).click()
    } catch (e) {
        return null
    }
}