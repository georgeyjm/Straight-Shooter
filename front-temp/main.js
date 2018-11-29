// let gradients = [
//     'linear-gradient(to right, #0c3483 20%, #a2b6df 80%, #6b8cce 80%, #a2b6df 80%);',
//     'linear-gradient(to right, #6a11cb 20%, #2575fc 80%)',
//     'linear-gradient(to right, #868686 20%, #000000 80%)',
//     'linear-gradient(to right, #868f96 20%, #596164 80%)',
//     'linear-gradient(to right, #09203f 20%, #537895 80%)'
// ];
// let gradient = gradients[Math.floor(Math.random() * gradients.length)];
//
// $('h1').css('background', '-webkit-' + gradient);
// $('h1').css('background', '-o-' + gradient);
// $('h1').css('background', '-moz-' + gradient);
// $('h1').css('background', gradient);
// $('h1').css('-webkit-background-clip', 'text');
// $('h1').css('-webkit-text-fill-color', 'transparent');

$('#search-box').on('input', e => {
    let query = $('#search-box').val();
    if (query !== '') $('#search-box').css({'border-bottom-left-radius': 0, 'border-bottom-right-radius': 0});
    else $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'});
})

.on('keypress', e => {
    if (e.which === 13) {
        console.log('Posting:', $('#search-box').val());
        return false;
    }
})

.autocomplete({
    lookup: ['Warrick Ingham', 'Daniel Mac Leon', 'David Hilbert', 'David Lin', 'Peter Mccombe', 'Melinda Mccombe', 'Deborah Kucinkas', 'Jianping Yang', 'Jason Borovick'],
    lookupLimit: 5,
    appendTo: $('.container'),
    beforeRender: () => $('#search-box').css({'border-bottom-left-radius': 0, 'border-bottom-right-radius': 0}),
    onHide: () => $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'}),
    onSelect: suggestion => console.log('Posting from select:', suggestion.value),
    onSearchComplete: (query, suggestions) => {
        if (suggestions.length === 0) $('#search-box').css({'border-bottom-left-radius': '4px', 'border-bottom-right-radius': '4px'});
    }
});
