
while(!$('input[name ="url_video"]')){
    console.log("alto")
}
url = $('input[name ="url_video"]').val()
url = url.replace("watch?v=", "embed/");   
item =  $('<iframe>', {
            src: url,
            id:  'myFrame',
            frameborder: 0,
            scrolling: 'no'
            })
$('.o_video_container').html(item)

$('input[name ="url_video"]').focusout(function() {
   
     url = $('input[name ="url_video"]').val()
     url = url.replace("watch?v=", "embed/");   
     item =  $('<iframe>', {
                 src: url,
                 id:  'myFrame',
                 frameborder: 0,
                 scrolling: 'no'
                 })
    $('.o_video_container').html(item)
 })