function get_resolute() {
    return {"width": window.innerWidth, "height": window.innerHeight}
}

function get_window_size() {
    return {"width": window.outerWidth, "height": window.outerHeight}
}

function get_workplace_size() {
    return {"width": window.innerWidth, "height": window.innerHeight}
}

function get_current_body_width() {
    return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.body.clientWidth)
}

function get_current_body_height() {
    return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.body.clientHeight)
}

function get_current_top_position() {
    return (window.pageYOffset || document.body.scrollTop) - (document.body.clientTop || 0)
}

function get_current_left_position() {
    return (window.pageXOffset || document.body.scrollLeft) - (document.body.clientLeft || 0)
}

function get_current_bottom_position() {
    return get_current_body_height() - get_workplace_size().height - get_current_top_position()
}

function get_current_right_position() {
    return get_current_body_width() - get_workplace_size().width - get_current_left_position()
}

function get_current_downline() {
    return get_workplace_size().height + get_current_top_position()
}

function get_current_rightline() {
    return get_workplace_size().width + get_current_left_position()
}

function get_current_workplace() {
    return [[get_current_left_position(), get_current_rightline()], [get_current_top_position(), get_current_downline()]]
}

function element_set_position_static(selector) {
    try {
        // document.getElementsByClassName(class_name)[0].style.position = 'static'
        get_elm_by_css(selector).style.position = 'static'
        return true
    }catch (e) {
        return true
    }
}