$(document).ready(function() {
    $('#clouds').pan({fps: 30, speed: 0.7, dir: 'left', depth: 10});
    $('#hill2').pan({fps: 30, speed: 2, dir: 'left', depth: 30});
    $('#hill1').pan({fps: 30, speed: 3, dir: 'left', depth: 70});
    $('#hill1, #hill2, #clouds').spRelSpeed(8);
});
