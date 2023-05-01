function insertPost(post) {
    let domTarget = $('#posts');
    let profid = $('#profile_id').attr('profile_id');
    let activeid = $('#profile_id').attr('active_id');
    let html = '<div class="post" postid="' + post.id + '">'+
                '<br><span>' + post.content +'</span><p>'

    if (post.likedBy.includes(parseInt(activeid))){
        html += '<a href="#" postid="' + post.id + '" class="downvote">Unlike | </a>'
    } else{
        html += '<a href="#" postid="' + post.id + '" class="upvote">Like | </a> '
    }
    html+=
    '<a href="#" data-bs-toggle="modal" data-bs-target="#exampleModal'+post.id+'">' +
      post.numLikes +
    '</a>' +
    '<div class="modal fade" id="exampleModal'+post.id+'" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">' +
      '<div class="modal-dialog">' +
        '<div class="modal-content">' +
          '<div class="modal-header">' +
            '<h5 class="modal-title" id="exampleModalLabel">Likes</h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>' +
          '</div>' +
          '<div class="modal-body" postid = "'+post.id+'"">' +
          '</div>' +
          '<div class="modal-footer">' +
            '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>' +
            '<button type="button" class="btn btn-primary">Save changes</button>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</div>';


    domTarget.prepend(html);

    if (!post.likedBy.includes(parseInt(activeid))){
        $('.upvote[postid=' + post.id + ']').click(function(event) {
            event.preventDefault();
            like(post.id);
        });
    }
    else{
        $('.downvote[postid=' + post.id + ']').click(function(event) {
            event.preventDefault();
            unlike(post.id);
        });
    }


    getLikes(post.id);
}

function insertProfile(profile, postid){
    console.log("GOT to insert")
    console.log(profile)
    console.log(postid)

    let modalContent = $('.modal-body[postid=' + postid +']');
    html = '<p>'+ profile.username + '</p>';

    modalContent.prepend(html);

}
function getLikes(postid){
    console.log("get likes")
    console.log(postid)
    $.ajax('/api/posts/' + postid + '/likes/', {
        method: 'GET',
        dataType: 'json',

        success: function(profiles) {
            clearProfiles(postid);
            profiles.forEach(function(profile) {
                insertProfile(profile, postid);
            });
        },

        error: function() {
            console.log('I have been disenfranchised!!!!!');
        }
    });



}

function like(postid){
    $.ajax('/api/posts/' + postid + '/like/', {
        method: 'POST',
        dataType: 'json',

        success: function(post) {
            console.log("success")
            let countElm = $('div.post[postid=' + post.id + ']').find('.votescount');
            countElm.html(post.numLikes);
            reloadPosts();
        },

        error: function() {
            console.log('I have been disenfranchised!!!!!');
        }
    });


}


function unlike(postid){
    $.ajax('/api/posts/' + postid + '/unlike/', {
        method: 'POST',
        dataType: 'json',

        success: function(post) {
            let countElm = $('div.post[postid=' + post.id + ']').find('.votescount');
            countElm.html(post.numLikes);
            reloadPosts();
        },

        error: function() {
            console.log('I have been disenfranchised!!!!!');
        }
    });
}


function clearPosts() {
    let domTarget = $('#posts');
    domTarget.html('');
}

function clearProfiles(postid) {
    let modalContent = $('.modal-body[postid=' + postid +']');
    modalContent.html('');
}

function getAllPosts() {
    let profid = $('#profile_id').attr('profile_id');
    $.ajax('/api/posts/?profile_id='+profid, {
        method: 'GET',
        dataType: 'json',

        success: function(posts) {
            clearPosts();
            posts.forEach(function(post) {
                insertPost(post);
            });
        },

        error: function() {
            $('#posts').html('Cannot load posts at this time.');
        }
    });
}

function reloadPosts() {
    $('#posts').html('Reloading...');
    window.setTimeout(getAllPosts, 0);
}

function sendPost() {
    let form = $('#post-form')[0];
    let data = new FormData(form);

    $('#post-btn').prop('disabled', true);

    $.ajax({
        type: 'POST',
        enctype: 'multipart/form-data',
        url: '/api/posts/',
        data: data,
        processData: false,
        contentType: false,
        success: reloadPosts,
        error: function() {
            $('#posts').html('Cannot post. Try again later.');
            $('#post-btn').prop('disabled', false);
        }
    });
}


// This is like document.ready().
$(function() {
    /*
    $('#reload-btn').click(function() {
        reloadPosts();
    });
    */

    $('#post-btn').click(function(event) {
        event.preventDefault();
        sendPost();
    });


    getAllPosts();
});

