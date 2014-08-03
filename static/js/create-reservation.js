!function( $ ) {

    var flight_date_picker = $('#id_flight_date').datepicker({
        onRender: function(date) {
            return date.valueOf() < new Date().valueOf() ? 'disabled' : '';
        }
    }).on('changeDate', function(ev) {
        flight_date_picker.datepicker('hide');
    });

}( window.jQuery );