(function () {
    let heatmap = h337.create({
        container: document.getElementById('heatmapContainer'),
        radius: 15,
    })
    let heatmapContainer = document.getElementById('heatmapContainerWrapper');
    heatmapContainer.onmousemove = heatmapContainer.ontouchmove = function (e) {
        e.preventDefault();
        let x = e.layerX
        let y = e.layerY
        if (e.touches) {
            x = e.touches[0].pageX
            y = e.touches[0].pageY
        }
        heatmap.addData({x: x, y: y, value: 50})
    };
    heatmapContainer.onclick = function (e) {
        let x = e.layerX
        let y = e.layerY
        heatmap.addData({x: x, y: y, value: 50})
    }
})()