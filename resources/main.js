$(document).ready(function() {
    $('#calculate').click(function() {
        // With URL encoding, 'frame%2504d' becomes 'frame%04d'.
        //generateFrames(
        //    '/Users/Sean/Documents/Programs/Projects/DropletMeasurement/resources/videos/5_min_25_C_0.1_M_186_mOsm_NaCl_and_Pure_water_in_2.0_mg_trans_DOPC_and_0.5_mg_CHOL_in_300_microliters_SqE_1001.avi',
        //    parseInt($('#seconds-per-frame').attr('value')),
        //));

        // With URL encoding, 'frame%2504d' becomes 'frame%04d'.
        //var videoFile = '/Users/Sean/Documents/Programs/Projects/DropletMeasurement/resources/videos/5_min_25_C_0.1_M_186_mOsm_NaCl_and_Pure_water_in_2.0_mg_trans_DOPC_and_0.5_mg_CHOL_in_300_microliters_SqE_1001.avi';
        var videoFile = '/Users/Sean/Documents/Programs/Projects/DropletMeasurement/resources/videos/10_min_25_C_0.1_M_186_mOsm_NaCl_and_Pure_water_in_2.0_mg_DOPC_and_0.5_mg_CHOL_in_300_microliters_SqE_1.avi';
        var secondsPerFrame = parseInt($('#seconds-per-frame').attr('value'));
        var framePath = '';
        updateStatus('Generating frames...');
        $.when($.get(`/generate-frames?video_file=${videoFile}&seconds_per_frame=${secondsPerFrame}`,
            function(response) {
                // TODO: Handle errors.
                updateStatus(response);
                framePath = response;
            }))
        .then(function() {
            $.get(`/find-circles?frame_path=${encodeURI(framePath)}`,
                function(response) {
                    updateStatus(response);
                });
        });

    });
});

function updateStatus(status) {
    $('#status').text(status);
    console.log(status);
}

function generateFrames(videoFile, secondsPerFrame) {
    updateStatus('Generating frames...');
    $.get(`/generate-frames?video_file=${videoFile}&seconds_per_frame=${secondsPerFrame}`,
        function(response) {
            updateStatus(response);
        });
}
