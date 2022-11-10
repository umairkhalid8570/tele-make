// called when select variant popup add to cart btn clicked
function CloseSelectModal() {
    $(".select-modal-backdrop").addClass('d-none');
    $(".select-modal").addClass('d-none');
}

// called when quick view popup add to cart btn clicked
function CloseQuickModal() {
    $(".quick-modal-backdrop").addClass('d-none');
    $(".quick-modal").addClass('d-none');
}

/*$(document).ready(function(){
    $('[data-toggle="popover"]').popover()
});*/

/* close popover */



$('body').on('click', function (e) {
    $('[data-toggle=popover]').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

/* close popover end */


function openSearchPopup() {
    $(".search-box").addClass("open");
}

function CartSidebar() {
    $("#cart_sidebar").addClass("toggled");
}
