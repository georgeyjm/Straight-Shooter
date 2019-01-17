function getUrlParam(key) {
    let result = new RegExp(`[\\?&]${key}=([^&#]*)`).exec(window.location.href);
	return result ? result[1] : null;
}

let form = $('#login-form');
form.submit(e => {
    $.post(form.attr('action'), form.serialize(), resp => {
        if (resp.code === 0) {
            let url = getUrlParam('url') || '/';
            url = url === window.location.pathname ? '/' : url;
            window.location.href = url;
        } else if (resp.code === 1) {
            form.append('<p class="login-error text-center">Incorrect username or password!</p>');
        } else if (resp.code === 2) {
            form.append('<p class="login-error text-center">Server busy! Try again later.</p>');
        }
     });
    return false;
});
