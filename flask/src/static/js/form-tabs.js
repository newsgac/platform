$(document).ready(function () {
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step-tab").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step-tab").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);

    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}


//according menu

$(document).ready(function()
{
    //Add Inactive Class To All Accordion Headers
    $('.accordion-header').toggleClass('inactive-header');

	//Set The Accordion Content Width
	var contentwidth = $('.accordion-header').width();
	$('.accordion-content').css({});

	//Open The First Accordion Section When Page Loads
	$('.accordion-header').first().toggleClass('active-header').toggleClass('inactive-header');
	$('.accordion-content').first().slideDown().toggleClass('open-content');

	// The Accordion Effect
	$('.accordion-header').click(function () {
		if($(this).is('.inactive-header')) {
			$('.active-header').toggleClass('active-header').toggleClass('inactive-header').next().slideToggle().toggleClass('open-content');
			$(this).toggleClass('active-header').toggleClass('inactive-header');
			$(this).next().slideToggle().toggleClass('open-content');
		}

		else {
			$(this).toggleClass('active-header').toggleClass('inactive-header');
			$(this).next().slideToggle().toggleClass('open-content');
		}
	});

	return false;
});


$(document).ready(function() {
    $('#experiment_svc').bootstrapValidator();
    $('#experiment_rf').bootstrapValidator();
});

$(function()
{
    $(document).on('click', '.btn-add', function(e)
    {
        e.preventDefault();

        var controlForm = $('#aspects'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);

        newEntry.find('input').val('');
        controlForm.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus"></span>');
    }).on('click', '.btn-remove', function(e)
    {
		$(this).parents('.entry:first').remove();

		e.preventDefault();
		return false;
	});
});

$(document).ready(function() {
    console.log("here")
    $('.features_div').hide();
    $('#data_source').change(function(){
        if($('#data_source').val().toLowerCase().indexOf("nltk") < 0) {
            $('.features_div').fadeIn();
        } else {
            $('.features_div').fadeOut();
        }
    });
});

$(document).ready(function() {
    $('.auto_data').change(function () {
        if ($('.auto_data').is(":checked")) {
            $('.details_div_data').fadeOut();
            return; }
       $('.details_div_data').fadeIn();
    });
    if ($('.auto_data').is(":checked")) {
            $('.details_div_data').fadeOut();
            return; }
});

$(document).ready(function() {
    $('.auto_feat').change(function () {
        if ($('.auto_feat').is(":checked")) {
            $('.details_div_feat').fadeOut();
            return; }
       $('.details_div_feat').fadeIn();
    });
    if ($('.auto_feat').is(":checked")) {
            $('.details_div_feat').fadeOut();
            return; }
});

$(document).ready(function() {
    $('.auto_alg').change(function () {
        if ($('.auto_alg').is(":checked")) {
            $('.details_div_alg').fadeOut();
            return; }
       $('.details_div_alg').fadeIn();
    });
    if ($('.auto_alg').is(":checked")) {
            $('.details_div_alg').fadeOut();
            return; }
});

$(document).ready(function() {
    $('#recommendation_table').DataTable(
    {
    columnDefs: [
//        {targets: 1, render: $.fn.dataTable.render.ellipsis(100, true)},
        {width: "8%", targets: 0 }, {width: "20%", targets: 1 }, {width: "30%", targets: 2 },
        ],

//    initComplete: function () {
//             // Setup - add a text input to each footer cell
//            $('#recommendation_table tfoot th').each( function () {
//                var title = $(this).text();
//                $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
//            } );
//            this.api().columns().every( function () {
//
//                var that = this;
//
//                $( 'input', this.footer() ).on( 'keyup change', function () {
//                    if ( that.search() !== this.value ) {
//                        that
//                            .search( this.value, false, false, true )
//                            .draw();
//                    }
//                } );
//                });
//
//        },
        stateSave: false,
        "scrollX": true,
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
} );

$(document).ready(function() {
    $('#explanations_table').DataTable(
    {
    columnDefs: [
//        {targets: 1, render: $.fn.dataTable.render.ellipsis(100, true)},
        {width: "8%", targets: 0 }, {width: "25%", targets: 1 }, {width: "15%", targets: 2 },
        ],

    initComplete: function () {
             // Setup - add a text input to each footer cell
            $('#explanations_table tfoot th').each( function () {
                var title = $(this).text();
                $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
            } );
            this.api().columns().every( function () {

                var that = this;

                $( 'input', this.footer() ).on( 'keyup change', function () {
                    if ( that.search() !== this.value ) {
                        that
                            .search( this.value, false, false, true )
                            .draw();
                    }
                } );
                });

        },
        stateSave: false,
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
} );


$(document).ready(function() {
    $('#combinations_table').DataTable(
    {
    columnDefs: [
//        {targets: 0, render: $.fn.dataTable.render.ellipsis(75, true)},
        {width: "55%", targets: 3 }, {width: "10%", targets: 2}, {width: "25%", targets: 0},
        ],

    initComplete: function () {
             // Setup - add a text input to each footer cell
            $('#combinations_table tfoot th').each( function () {
                var title = $(this).text();
                $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
            } );
            this.api().columns().every( function () {

                var that = this;

                $( 'input', this.footer() ).on( 'keyup change', function () {
                    if ( that.search() !== this.value ) {
                        that
                            .search( this.value )
                            .draw();
                    }
                } );
                });

        },
        stateSave: false,
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
} );


$(document).ready(function() {
    $('#experiments_comparison_table').DataTable(
    {
    columnDefs: [
        {targets: 1, render: $.fn.dataTable.render.ellipsis(75, true)},
        {width: "10%", targets: 0 },
        {width: "30%", targets: 1 },
        ],
        initComplete: function () {
            this.api().columns().every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo( $(column.footer()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );

                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                })
                })
        },
        stateSave: true,
        responsive: true,
        "scrollX": true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
} );


$(document).ready(function() {
    $('#data_sources_table').DataTable(
    {
    columnDefs: [
        {targets: 4, render: $.fn.dataTable.render.ellipsis(75, true)},
        {width: "8%", targets: 1 },
        {width: "5%", targets: 2 },
        {width: "7%", targets: 7 },
         ],
    initComplete: function () {
            this.api().columns().every( function () {
                var column = this;
                var select = $('<select><option value=""></option></select>')
                    .appendTo( $(column.footer()).empty() )
                    .on( 'change', function () {
                        var val = $.fn.dataTable.util.escapeRegex(
                            $(this).val()
                        );

                        column
                            .search( val ? '^'+val+'$' : '', true, false )
                            .draw();
                    } );

                column.data().unique().sort().each( function ( d, j ) {
                    select.append( '<option value="'+d+'">'+d+'</option>' )
                })
                })
                },
        stateSave: true,
        "scrollX": true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]]
    } );
} );