$.get('/get-teachers', resp => {
    let allTeachers;
    if (resp.code === 0) allTeachers = resp.data;
    else allTeachers = []; // Placeholder, should retry or something

    $('#search-box').autocomplete({
        lookup: allTeachers,
        lookupLimit: 5,
        appendTo: $('#main-content'),
        beforeRender: () => $('#search-box').css({'border-bottom-left-radius': 0, 'border-bottom-right-radius': 0}),
        onHide: () => $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'}),
        onSelect: suggestion => window.location.href = '/teacher/' + suggestion.value,
        onSearchComplete: (query, suggestions) => {
            if (suggestions.length === 0) $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'});
        }
    });
});

$('#search-box').on('input', e => {
    let query = $('#search-box').val();
    if (query !== '') $('#search-box').css({'border-bottom-left-radius': 0, 'border-bottom-right-radius': 0});
    else $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'});
})

.on('keypress', e => {
    if (e.which === 13) {
        window.location.href = '/teacher/' + $('#search-box').val();
        return false;
    }
});
