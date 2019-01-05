// Remove iOS tap grey box
document.addEventListener('touchstart', () => {}, true);

$('#submit-button').click(() => {
    let rating = parseFloat($('.stars-container :checked').val()) * 2;
    let comment = $('#comment').val();
    let classId = $('#classes-dropdown').val();

    let formData = {
        teacher_id: TEACHER_ID,
        class_id: classId,
        rating: rating,
        comment: comment
    };

    $.post('/rate', formData, resp => {
        console.log(resp)
        if (resp.code === 0) {
            let teacher_name = window.location.pathname.split('/')[2];
            window.location.href = '/teacher/' + teacher_name;
        } else if (resp.code === 1) {
            form.append('<p class="login-error text-center">Incorrect username or password!</p>');
        } else if (resp.code === 2) {
            form.append('<p class="login-error text-center">Server busy! Try again later.</p>');
        }
     });

    // do post and things
});
