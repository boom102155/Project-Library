$(document).ready(function() {
	$.fn.datepicker.defaults.language = 'th';

	
	$('.today').datepicker({
		format: 'yyyy-mm-dd',
	    autoclose: true
	}).datepicker("setDate", "0");

	$('.fromdate').datepicker({
	    format: 'yyyy-mm-dd',
	    autoclose: true
	}).on('changeDate', function (selected) {
    var minDate = new Date(selected.date.valueOf());
    $('.todate').datepicker('setStartDate', minDate);
	});

	$('.todate').datepicker({
	    format: 'yyyy-mm-dd',
	    autoclose: true
	}).on('changeDate', function (selected) {
        var minDate = new Date(selected.date.valueOf());
        $('.fromdate').datepicker('setEndDate', minDate);
    });

	$('.fromdate').datepicker().bind("change", function () {
	    calculate();
	});
	$('.todate').datepicker().bind("change", function () {
	    calculate();
	});

	function calculate() {
	    var d1 = $('.fromdate').datepicker('getDate');
	    var d2 = $('.todate').datepicker('getDate');
	    var oneDay = 24*60*60*1000;
	    var diff = 0;
	    if (d1 != null && d2 != null) {
	    	diff = Math.round(Math.abs((d2.getTime() - d1.getTime())/(oneDay)+1));
	    	
	    }
	    $('.dateresult').val(diff);
	    
	}
});