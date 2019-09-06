$(document).ready(function() {
    $('li.active').removeClass('active');
    $('a[href="' + location.pathname + '"]').closest('li').addClass('active');

    $('a').removeClass('active');
    $('a[href="' + location.pathname + '"]').closest('a').addClass('active');

    // var showBottomMenu = $(window).height() * 1.1;
    var showBottomMenu = 60
    $('#bootom-menu').each(function() {
        if ($(window).scrollTop() <= showBottomMenu) $(this).fadeOut('slow');
        var scrollDiv = $(this);
        $(window).scroll(function() {
            if ($(window).scrollTop() <= showBottomMenu) {
                console.log('SDDSDSD')
                $(scrollDiv).fadeOut('slow');
            } else {
                $(scrollDiv).fadeIn('slow');
            }
        });
    });
    $('#go-top').each(function() {
        $(this).click(function() {
            $('html, body').animate({scrollTop: 0}, 'slow')
        });
    });

});
