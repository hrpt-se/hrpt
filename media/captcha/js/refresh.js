$(document).ready(function() {
    $('.captcha-refresh').click(function () {
        var $form = $(this).parents('form');
        var url = location.protocol + "//" + window.location.hostname + ":"
            + location.port + "/captcha/refresh/";

        $.getJSON(url, {}, function (json) {
            $form.find('input[name="captcha_0"]').val(json.key);
            $form.find('img.captcha').attr('src', json.image_url);
        });

        return false;
    });
});