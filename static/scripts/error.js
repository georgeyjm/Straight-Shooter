for (let i = 0; i < 5; i++) {
    setTimeout(() => {
        $('#countdown').html(`Returning to main page in ${5 - i} seconds.`)
    }, 1000 * i);
}

setTimeout(() => {
    window.location.href = '/';
}, 5000);
