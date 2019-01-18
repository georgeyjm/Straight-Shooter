function getUrlParam(key) {
    let result = new RegExp(`[\\?&]${key}=([^&#]*)`).exec(window.location.href);
	return result ? result[1] : null;
}

let form = $('#login-form');
form.submit(e => {
    $('#login-msg').html('');
    $.post(form.attr('action'), form.serialize(), resp => {
        if (resp.code === 0) {
            let url = getUrlParam('url') || '/';
            url = url === window.location.pathname ? '/' : url;
            window.location.href = url;
        } else if (resp.code === 1) {
            $('#login-msg').html('Incorrect username or password!');
        } else if (resp.code === 2) {
            $('#login-msg').html('Server busy! Try again later.');
        }
     });
    return false;
});
