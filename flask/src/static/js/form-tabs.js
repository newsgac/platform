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

    $(".next-step").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

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
    $('#experiment_svm').bootstrapValidator();
    $('#experiment_dt').bootstrapValidator();
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

    $('input[type=checkbox][id=auto_pp]').change(function(){
        if($(this).is(':checked')) {
            $('input[type=checkbox][id=stemming]').prop("disabled",true);
            $('input[type=checkbox][id=stemming]').prop("checked",false);
            $('input[type=checkbox][id=sw_removal]').prop("disabled",true);
            $('input[type=checkbox][id=sw_removal]').prop("checked",false);
            $('input[type=checkbox][id=avg_sent_length]').prop("disabled",true);
            $('input[type=checkbox][id=avg_sent_length]').prop("checked",false);
            $('input[type=checkbox][id=perc_exclamation_mark]').prop("disabled",true);
            $('input[type=checkbox][id=perc_exclamation_mark]').prop("checked",false);
            $('input[type=checkbox][id=perc_adjectives]').prop("disabled",true);
            $('input[type=checkbox][id=perc_adjectives]').prop("checked",false);
            $('#stemming_div').addClass("disabled");
            $('#sw_removal_div').addClass("disabled");
            $('#avg_sent_length_div').addClass("disabled");
            $('#perc_exclamation_mark_div').addClass("disabled");
            $('#perc_adjectives_div').addClass("disabled");
        } else {
            $('input[type=checkbox][id=stemming]').prop("disabled",false);
            $('input[type=checkbox][id=sw_removal]').prop("disabled",false);
            $('input[type=checkbox][id=avg_sent_length]').prop("disabled",false);
            $('input[type=checkbox][id=perc_exclamation_mark]').prop("disabled",false);
            $('input[type=checkbox][id=perc_adjectives]').prop("disabled",false);
            $('#stemming_div').removeClass("disabled");
            $('#sw_removal_div').removeClass("disabled");
            $('#avg_sent_length_div').removeClass("disabled");
            $('#perc_exclamation_mark_div').removeClass("disabled");
            $('#perc_adjectives_div').removeClass("disabled");
        }
    });
});

$(document).ready(function() {

    $('input[type=checkbox][id=auto_alg]').change(function(){
        if($(this).is(':checked')) {
            $('#penalty_parameter_c_div').prop("disabled", true);
            $('#penalty_parameter_c_div').addClass("disabled");
            $('#kernel_div').addClass("disabled");
            $('#probability_div').addClass("disabled");
            $('#random_state_div').addClass("disabled");
        } else {
            $('#penalty_parameter_c_div').removeClass("disabled");
            $('#kernel_div').removeClass("disabled");
            $('#probability_div').removeClass("disabled");
            $('#random_state_div').removeClass("disabled");
        }
    });
});

$(document).ready(function() {

    $('input[type=checkbox][id=auto_alg]').change(function(){
        if($(this).is(':checked')) {
            $('#criterion_div').prop("disabled", true);
            $('#criterion_div:input').attr("disabled", true);
            $('#criterion_div').addClass("disabled");
            $('#splitter_div').addClass("disabled");
            $('#min_samples_split_div').addClass("disabled");
            $('#min_samples_leaf_div').addClass("disabled");
            $('#max_features_div').addClass("disabled");
            $('#random_state_div').addClass("disabled");
        } else {
            $('#criterion_div:input').removeAttr('disabled');
            $('#criterion_div').removeClass("disabled");
            $('#splitter_div').removeClass("disabled");
            $('#min_samples_split_div').removeClass("disabled");
            $('#min_samples_leaf_div').removeClass("disabled");
            $('#max_features_div').removeClass("disabled");
            $('#random_state_div').removeClass("disabled");
        }
    });
});
