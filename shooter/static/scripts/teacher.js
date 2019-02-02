/* User interaction */



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
    let formData = {
        teacher_id: TEACHER_ID
    };
    $.post('/get-classes', formData, resp => {
        if (resp.code === 0) classes = resp.data;
        f();
    });
}

function loadRatings(offset) {
    console.log('load ratings');
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
                <div class="wrapper">
                <div class="comment">
                <div class="comment-text">
                    <h3>This teacher is sensational!</h3>
                    <p class="comment-content">${ rating[2] }</p>
                    <div class="secondary-info text-italics" style="text-align: right">${ timeago.format(rating[5] * 1000) }</div>
                </div>

                <div class="vote-section">
                    <p class="upvote">${ rating[3] }</p><a class="vote-btn upvote"><i class="far fa-thumbs-up fa-2x"></i></a>
                    <a class="vote-btn downvote"><i class="far fa-thumbs-down fa-2x"></i></a>
                    <p class="downvote">${ rating[4] }</p>
                </div>
                </div>
                </div>
                `).hide().appendTo('#main-content').fadeIn().each(function() {
                    addRatingCallback();
                });
                replies = rating[6]
                if (replies != null) {
                    for (let reply of replies) {
                        $(`
                        <div class="reply">
                            <div class="show-reply"><i class="material-icons show-click">expand_more</i>
                                <p>Hide Replies</p>
                            </div>
    
                            <div class="collapsible">
                                <div class="comment">
    
                                    <div class="comment-text">
                                        <p class="comment-content">${ reply[2] }</p>
                                        <div class="secondary-info text-italics" style="text-align: right">${ timeago.format(reply[5] * 1000) }</div>
                                    </div>
    
                                </div>
                                
                            </div>
                        </div>
                        `).appendTo('#main-content div.wrapper:last').each(function() {
                            addRepliesCallback();
                        });
                    }
                    
                }
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

function addRatingCallback() {
    $('.vote-btn:last').click(function () {
        console.log("Called callback!");
        if ($(this).children('i').hasClass('btn-checked')) {
            $(this).children('i').removeClass('btn-checked');
        } else {
            $(this).children('i').addClass('btn-checked');
        }
    });
}
function addRepliesCallback() {

    $('.show-reply:last').click(function () {
        var content = this.nextElementSibling;

        if ($('.show-click').text() === "expand_more") {
            $('.show-click').text("expand_less");
            $('.show-reply p').text("Show replies");
            content.style.display = "none";

        } else {
            $('.show-click').text("expand_more");
            $('.show-reply p').text("Hide replies");
            content.style.display = "block";
        }
    });
    console.log('Callbacks added');
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