$(document).ready(function () {
    $('#clouds').pan({fps: 30, speed: 0.7, dir: 'left', depth: 10});
    $('#hill2').pan({fps: 30, speed: 2, dir: 'left', depth: 30});
    $('#hill1').pan({fps: 30, speed: 3, dir: 'left', depth: 70});
    $('#hill1, #hill2, #clouds').spRelSpeed(8);
    // spritely methods...
    $('#bird')
        .sprite({fps: 9, no_of_frames: 3})
        .isDraggable({
            start: function () {
                if (!$.browser.msie) {
                    $('#bird').fadeTo('fast', 0.7);
                }
            },
            stop: function () {
                if (!$.browser.msie) {
                    $('#bird').fadeTo('slow', 1);
                }
            }
        });
    if (document.location.href.indexOf('/tools') == -1) {
        $('#bird')
            .activeOnClick()
            .active();
    }
    $('#bird2')
        .sprite({fps: 12, no_of_frames: 3})
        .isDraggable({
            start: function () {
                if (!$.browser.msie) {
                    $('#bird2').fadeTo('fast', 0.7);
                }
            },
            stop: function () {
                if (!$.browser.msie) {
                    $('#bird2').fadeTo('slow', 1);
                }
            }
        })
        .activeOnClick();


});
