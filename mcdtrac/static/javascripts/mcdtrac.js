/**
 * GET the selected xform
 * @param xform - selected xform
 */
function select_xform(xform){
	$.get('/mcdtrac/' + xform.value + '/submissions/');
}
