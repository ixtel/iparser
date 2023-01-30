(function () {
    let cursor_trail_css = '.cursor_trail_points { position: absolute; z-index:999999; height: 6px; width: 6px; border-radius: 3px; background: teal; }'
    let head = document.head || document.getElementsByTagName('head')[0]
    let style = document.createElement('style')

    style.type = 'text/css'
    if (style.styleSheet) {
        style.styleSheet.cssText = cursor_trail_css
    } else {
        style.appendChild(document.createTextNode(cursor_trail_css))
    }
    head.appendChild(style)

    // var mouse_trail_scr = document.createElement('script');
    // mouse_trail_scr.type = 'text/javascript';
    // mouse_trail_scr.src=
    let cursor_trail_dots = []
    let cursor_trail_position = {
            x: 0,
            y: 0
        }

    let cursor_trail_dot = function () {
        this.x = 0
        this.y = 0
        this.node = (function () {
            let n = document.createElement("div")
            n.className = "cursor_trail_points"
            document.body.appendChild(n)
            return n
        }())
    }

    cursor_trail_dot.prototype.draw = function () {
        this.node.style.left = this.x + "px"
        this.node.style.top = this.y + "px"
    }

    for (let i = 0; i < 8; i++) {
        let d = new cursor_trail_dot()
        cursor_trail_dots.push(d)
    }

    function cursor_trail_draw() {
        let x = cursor_trail_position.x
        let y = cursor_trail_position.y

        cursor_trail_dots.forEach(function (dot, index, dots) {
            let nextDot = cursor_trail_dots[index + 1] || cursor_trail_dots[0]

            dot.x = x
            dot.y = y
            dot.draw()
            x += (nextDot.x - dot.x) * .45
            y += (nextDot.y - dot.y) * .45
        })
    }

    addEventListener("mousemove", function (event) {
        let offset_px = 7
        cursor_trail_position.x = event.pageX + offset_px
        cursor_trail_position.y = event.pageY + offset_px
    })

    function cursor_trail_animate() {
        cursor_trail_draw()
        requestAnimationFrame(cursor_trail_animate)
    }

    cursor_trail_animate()
})()

// document.body.appendChild(mouse_trail_scr);