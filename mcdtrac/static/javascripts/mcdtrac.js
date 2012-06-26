/**
 * GET the selected xform
 * @param xform - selected xform
 */
function select_xform(xform){
	$.post('/mcdtrac/' + xform.value + '/submissions/', {'form_id':xform.value}, function(data) {
		  $('#object_list').html(data)
	});
}
