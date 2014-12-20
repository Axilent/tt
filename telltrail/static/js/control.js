/* ================================== */
/* = Scripts for Data Control Panel = */
/* ================================== */

function show_advanced() {
    $('#advanced').fadeIn();
}

function hide_advanced() {
    $('#advanced').fadeOut();
}

function edit_personal_info() {
    $('#personal_info').load('/control/info/edit/');
}

function view_personal_info() {
    $('#personal_info').load('/control/info/');
}

function edit_policy() {
    $('#data_policy').load('/control/policy/edit/');
}

function view_policy() {
    $('#data_policy').load('/control/policy/');
}

function add_identity() {
    $('#identity_panel').load('/control/identity/add/').fadeIn();
}

function close_dialog(dialog) {
    $('#'+dialog).fadeOut();
}

function delete_identity(claim_id) {
    $('#identity_list').load('/control/identity/'+claim_id+'/delete/');
}

function add_exception() {
    $('#exception_panel').load('/control/exception/add/').fadeIn();
}

function delete_exception(exception_id) {
    $('#exception_list').load('/control/exception/'+exception_id+'/delete/');
}

function add_specific() {
    $('#specific_panel').load('/control/specific/add/').fadeIn();
}

function delete_specific_policy(policy_id) {
    $('#policy_list').load('/control/specific/'+policy_id+'/delete/');
}