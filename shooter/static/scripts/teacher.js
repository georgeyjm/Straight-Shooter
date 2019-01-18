let lazyLoad = true;
let offset = 0;
let loadingAsync = false;
let classes = {};

function ratingLevel(rating) {
    if (rating > 5.0) return '';
    else if (rating >= 4.0) return 'good';
    else if (rating >= 3.0) return 'medium';
    else if (rating >= 0.0) return 'bad';
    else return '';
}

function getClasses(f) {
    let formData = {teacher_id: TEACHER_ID};
    $.post('/get-classes', formData, resp => {
        if (resp.code === 0) classes = resp.data;
        f();
    });
}

function loadRatings(offset) {
    let formData = {
        teacher_id: TEACHER_ID,
        offset: offset
    };

    loadingAsync = true;
    $.post('/get-ratings', formData, resp => {
        if (resp.code === 0) {
            let allRatings = resp.data;
            for (let rating of allRatings) {
                $(`
                    <div class='rating-container'>
                      <div class='rating-rating-container'>
                        <p class='rating ${ ratingLevel(rating[1] / 2) }'>${ (rating[1] / 2).toFixed(1) }</p>
                        <p class='secondary-info'>${ classes[rating[0]] }</p>
                      </div>
                      <div>
                        <p class='text-body'>${ rating[2] }</p>
                        <p class='secondary-info text-italics'>${ timeago.format(rating[5] * 1000) }</p>
                      </div>
                    </div>
                `).hide().appendTo('#main-content').fadeIn();
            }

            if (allRatings.length === 0) {
                lazyLoad = false;

                if (offset === 0) {
                    $('#main-content').append(`<p class='rating-container'>There are no ratings yet.</p>`);
                }
            }
        }

        loadingAsync = false;
    });
}


let overallRating = $('#teacher-overall').html();

if (overallRating !== 'N/A') {
    overallRating = parseFloat(overallRating);
    $('#teacher-overall').addClass(ratingLevel(overallRating));
}


getClasses(() => loadRatings(offset));

$(window).scroll(e => {
    if (lazyLoad && !loadingAsync && $(this).scrollTop() >= $(document).height() - $(this).height() - 60) {
        loadRatings(++offset);
    }
});
