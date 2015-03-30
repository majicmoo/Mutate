
$(function () {
    $('.load_content').on('click', function (e) {
        elem = $(this); // elem = $(e.target)
        url = elem.attr("data-url");
        target = elem.attr("data-target");
        web2py_ajax_page("GET", url, "", target);
        return false; // e.preventDefault()
    });
});
