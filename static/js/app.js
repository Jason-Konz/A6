function insertPost(post) {
    let domTarget = $('#posts');
    let profid = $('#profile_id').attr('val');
    let html = '<div class="post" postid="' + post.id + '">'+
                '<br><span>' + post.content +'</span><p>'

    if (post.likedBy.includes(parseInt(profid))){
        html += '<a href="#" postid="' + post.id + '" class="downvote">downvote</a>'
    } else{
        html += '<a href="#" postid="' + post.id + '" class="upvote">upvote</a> '
    }
    html+= '<span class="votescount">(# of Likes: ' + post.numLikes + ')</span></p>'

    domTarget.append(html);

    $('.upvote[postid=' + post.id + ']').click(function(event) {
        event.preventDefault();
        like(post.id);
    });

    $('.downvote[postid=' + post.id + ']').click(function(event) {
        event.preventDefault();
        unlike(post.id);
    });
}

function like(postid){
    $.ajax('/api/posts/' + postid + '/like/', {
        method: 'POST',
        dataType: 'json',

        success: function(post) {
            let countElm = $('div.post[postid=' + post.id + ']').find('.votescount');
            countElm.html(post.numLikes);
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

function getAllPosts() {
    console.log("We are here");
    let profid = $('#profile_id').attr('val');
    console.log("ahhhh")
    console.log(profid);
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
    window.setTimeout(getAllPosts, 2000);
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

