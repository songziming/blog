// 计算 offsetTop 的时候，里面不包含 margin，因此我们这里需要把 margin 计算进来
var sidebar;
var min_y;
var max_y;
window.onload = function() {
    sidebar    = document.getElementById("sidebar");
    var header = document.getElementById("header");
    var footer = document.getElementById("footer");
    var limit  = Math.max(document.body.scrollHeight,
                          document.body.offsetHeight,
                          document.documentElement.clientHeight,
                          document.documentElement.scrollHeight,
                          document.documentElement.offsetHeight);
    min_y = header.clientHeight + 16;   // 16 is sidebar.margin_top - sticky_margin
    max_y = limit - footer.clientHeight - sidebar.clientHeight - 16;

    if (max_y > min_y) {
        window.onscroll = function() {
            if (window.pageYOffset >= max_y) {
                // stick to the footer
                sidebar.classList.add("bottom");
                sidebar.classList.remove("sticky");
            } else if (window.pageYOffset >= min_y) {
                // stick to the viewport
                sidebar.classList.add("sticky");
                sidebar.classList.remove("bottom");
            } else {
                // stick to nothing
                sidebar.classList.remove("sticky");
                sidebar.classList.remove("bottom");
            }
        };
    }
};