$(document).ready(function() {
    const maxTripTypes = 2;
    let selectedTripTypes = new Set();

    $('.trip-type-box').click(function() {
        if ($(this).hasClass('disabled')) {
            return;
        }

        const tripType = $(this).data('type');
        
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
            selectedTripTypes.delete(tripType);
            updateTripTypeBoxes();
        } else if (selectedTripTypes.size < maxTripTypes) {
            $(this).addClass('selected');
            selectedTripTypes.add(tripType);
            updateTripTypeBoxes();
        }
    });

    function updateTripTypeBoxes() {
        $('.trip-type-box').each(function() {
            if (!$(this).hasClass('selected') && selectedTripTypes.size >= maxTripTypes) {
                $(this).addClass('disabled');
            } else {
                $(this).removeClass('disabled');
            }
        });
    }
});
