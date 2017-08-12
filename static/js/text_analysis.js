var text_max = 200;
var API_URL = 'http://localhost:5000/'
$('#count_message').html(text_max + ' remaining');

$('#textarea').keyup(function() {
  var text_length = $('#textarea').val().length;
  var text_remaining = text_max - text_length;

  $('#count_message').html(text_remaining + ' remaining');
});

$('#text-analysis').click(function() {
    var text = $('#textarea').val();
    $("#success").hide();
    $("#chartContainer").empty();
    $("result").empty();
    $("#error").hide();
    if (text) {
        $.ajax({
                url: API_URL + 'text_analysis',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({data: text}),
                success: function(response) {
                    text_analysis = response.text_analysis;
                    $("#result").html($("<h3>Text analysis results:</h3>"));
                    ['adjectives', 'nouns', 'verbs', 'sentences count', 'words count', 'words', 'most_common_10'].forEach(function (key) {
                     if(key === 'most_common_10') {
                        data = [];
                        words = text_analysis[key];
                        Object(words).forEach(function(word) {
                            data.push({y: word[1], legendText: word[0], indexLabel:word[0]})
                        });
                        drawChart(data);
                     }
                     else {
                         $("#result").append($("<p style='font-size:large;'><b>" + key + "</b>: " + text_analysis[key] +"</p>"));
                         }
                    });
                },
                error: function(response) {
                    console.log(response);
                    $("#error").html($("<p></p>").text(error.message || 'Failed'));
                    $("#success").hide();
                    $("#error").show();
                }
            })
    }
});

$('#spell-check').click(function() {
    var text = $('#textarea').val();
    $("#result").empty();
    $("#chartContainer").empty();
    $("#success").hide();
    $("#error").hide();
    if (text) {
        $.ajax({
                url: API_URL + 'spell_check',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({data: text}),
                success: function(response) {
                    console.log(response);
                    words = response.spell_check;
                    original_text = $('#textarea').val().toLowerCase();
                    original_words = original_text.split(/\s*\b\s*/)
                    var hasError = false;
                    var corrected_words = []
                    for(var i = 0; i < original_words.length; i++) {
                        if (words[original_words[i]] && words[original_words[i]] && words[original_words[i]][0] !== original_words[i]) {
                            hasError = true;
                            corrected_words.push([original_words[i], words[original_words[i]]])
                        }
                    }
                    if(!hasError) {
                        $("#success").html($("<p></p>").text('Spelling is OK'));
                        $("#success").show();
                    } else {
                        $("#result").html($("<h3>Spelling corrections:</h3>"));
                        for(var i = 0; i < Object.keys(corrected_words).length; i++){
                            $("#result").append($("<p>" + "<span class='original'>" + corrected_words[i][0] + "</span>" + " &#8594; " + "<span class='corrected'>" + corrected_words[i][1] + "</span> </p>"));
                        }
                    }
//                    console.log(corrected_words, hasError);
                },
                error: function(response) {
                    console.log(response);
                    $("#error").html($("<p></p>").text(error.message || 'Failed'));
                    $("#success").hide();
                    $("#error").show();
                }
            })
    }
});

$('#sentiment-analysis').click(function() {
    var text = $('#textarea').val();
    $("#chartContainer").empty();
    $("#success").hide();
    $("#error").hide();
    $('#naive-bag').empty();
    $('#naive-best').empty();
    $('#svm').empty();
    if (text) {
        $.ajax({
                url: API_URL + 'sentiment_analysis',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({data: text}),
                success: function(response) {
                    var classifiers = response.classifiers;
                    var naive_bag_of_words_prob = classifiers.naive_bag_of_words.reduce((x, y) => x + y) / classifiers.naive_bag_of_words.length;
                    var naive_best_words_prob = classifiers.naive_best_words.reduce((x, y) => x + y) / classifiers.naive_best_words.length;
                    var naive_bag_of_words_res = naive_bag_of_words_prob >= 0.5 ? 'pos': 'neg';
                    var naive_best_words_res = naive_best_words_prob >= 0.5 ? 'pos': 'neg';
                    if (naive_bag_of_words_res === 'neg') {
                        naive_bag_of_words_prob = 1 - naive_bag_of_words_prob;
                    }
                    if (naive_best_words_res === 'neg') {
                        naive_best_words_prob = 1 - naive_best_words_prob;
                    }
                    var svm_prob = classifiers.svm.reduce((x, y) => x + y) / classifiers.svm.length;
                    var svm_res = svm_prob >= 0.5 ? 'pos': 'neg';
                    if (svm_res === 'neg') {
                        svm_prob = 1 - svm_prob;
                    }
                    $('#naive-bag').append($("<td>Naive Bayes (bag of words)</td><td>" + naive_bag_of_words_res + "</td><td>" + naive_bag_of_words_prob + "</td>"));
                    $('#naive-best').append($("<td>Naive Bayes (best words)</td><td>" + naive_best_words_res + "</td><td>" + naive_best_words_prob + "</td>"));
                     $('#svm').append($("<td>SVM (Support vector machine)</td><td>" + svm_res + "</td><td>" + svm_prob + "</td>"));
//                    $("#result").append($("<p style='font-size:large'><b>Naive Bayes(Model: bag of words): </b>" +  naive_bag_of_words_res + naive_bag_of_words_prob + "</p>"));
//                    $("#result").append($("<p style='font-size:large'><b>" + "Naive Bayes(Model: best words)" + ":</b> " +  naive_best_words_res + naive_best_words_prob + "</p>"));
//                    $("#result").append($("<p style='font-size:large'><b>" + "SVM(Support vector machine)" + ": </b>" +  svm_res + svm_prob + "</p>"));
                },
                error: function(response) {
                    console.log(response);
                    $("#error").html($("<p></p>").text(error.message || 'Failed'));
                    $("#success").hide();
                    $("#error").show();
                }
            })
    }
});

function drawChart(inputData) {
chartContainer
	var chart = new CanvasJS.Chart("chartContainer",
	{
		title:{
			text: "Most common words"
		},
                animationEnabled: true,
		legend:{
			verticalAlign: "bottom",
			horizontalAlign: "center"
		},
		data: [
		{
			indexLabelFontSize: 20,
			indexLabelFontFamily: "Monospace",
			indexLabelFontColor: "darkgrey",
			indexLabelLineColor: "darkgrey",
			indexLabelPlacement: "outside",
			type: "pie",
			showInLegend: true,
			toolTipContent: "{y} - <strong>#percent%</strong>",
			dataPoints: inputData
        }
        ]
    });
    chart.render();
}