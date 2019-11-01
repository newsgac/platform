import pytest

from newsgac.data_sources.models import DataSource
from newsgac.data_sources.parsers.newsgac import NewsgacFormatParser


@pytest.fixture()
def data_source_balanced_10(test_user, dataset_balanced_10):
    DataSource.objects.all().delete()
    data_source = DataSource(
        user=test_user,
        filename="bla.txt",
        description="For testing",
        display_title="test dataset",
        file=dataset_balanced_10
    )
    data_source.save()
    data_source.articles = NewsgacFormatParser.get_articles_from_data_source(data_source)
    return data_source


@pytest.fixture()
def list_frog_features():
    return\
        [{'polarity': 0.3317708333333334, 'avg_sentence_length': 14, 'question_marks_perc': 0.0,
                'unique_named_entities': 0.45698924731182794, 'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0,
                'subjectivity': 0.7104166666666666, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 2, 'modal_adverbs_perc': 0.0, 'sentences': 19,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6666666666666666, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.010752688172043012, 'intensifiers_perc': 0.0},
               {'polarity': 0.06825396825396826, 'avg_sentence_length': 18, 'question_marks_perc': 0.007849293563579277,
                'unique_named_entities': 0.34782608695652173, 'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0,
                'subjectivity': 0.5162698412698413, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 7, 'modal_adverbs_perc': 0.0, 'sentences': 35,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6499215070643642, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.04552590266875981, 'intensifiers_perc': 0.0},
               {'polarity': 0.07137681159420291, 'avg_sentence_length': 15, 'question_marks_perc': 0.0,
                'unique_named_entities': 0.3850415512465374, 'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0,
                'subjectivity': 0.4427536231884057, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 10, 'modal_adverbs_perc': 0.0, 'sentences': 36,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6333333333333333, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.07017543859649122, 'intensifiers_perc': 0.0},
               {'polarity': 0.07261695906432748, 'avg_sentence_length': 19, 'question_marks_perc': 0.0,
                'unique_named_entities': 0.3220338983050847, 'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0,
                'subjectivity': 0.4197222222222221, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 4, 'modal_adverbs_perc': 0.0, 'sentences': 44,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6306413301662708, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.010688836104513063, 'intensifiers_perc': 0.0},
               {'polarity': 0.12282051282051276, 'avg_sentence_length': 14,
                'question_marks_perc': 0.0021470746108427268, 'unique_named_entities': 0.26649528706083975,
                'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.001610305958132045,
                'subjectivity': 0.5295014245014248, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 7, 'modal_adverbs_perc': 0.0, 'sentences': 130,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6264090177133655, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.008051529790660225, 'intensifiers_perc': 0.0},
               {'polarity': 0.07929597701149424, 'avg_sentence_length': 15, 'question_marks_perc': 0.0,
                'unique_named_entities': 0.4090909090909091, 'modal_verbs_perc': 0.0,
                'exclamation_marks_perc': 0.0023094688221709007, 'subjectivity': 0.5637931034482758,
                'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0, 'pronoun_3_perc': 0.0, 'direct_quotes': 5,
                'modal_adverbs_perc': 0.0, 'sentences': 56, 'adjectives_perc': 0.0,
                'named_entities_perc': 0.6096997690531177, 'pronoun_1_perc': 0.0, 'pronoun_2_perc': 0.0,
                'digits_perc': 0.053117782909930716, 'intensifiers_perc': 0.0},
               {'polarity': 0.0026041666666666644, 'avg_sentence_length': 12,
                'question_marks_perc': 0.00641025641025641, 'unique_named_entities': 0.24896694214876033,
                'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0, 'subjectivity': 0.490763888888889,
                'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0, 'pronoun_3_perc': 0.0, 'direct_quotes': 0,
                'modal_adverbs_perc': 0.0, 'sentences': 116, 'adjectives_perc': 0.0,
                'named_entities_perc': 0.6894586894586895, 'pronoun_1_perc': 0.0, 'pronoun_2_perc': 0.0,
                'digits_perc': 0.018518518518518517, 'intensifiers_perc': 0.0},
               {'polarity': 0.02483739837398374, 'avg_sentence_length': 16,
                'question_marks_perc': 0.0043076923076923075, 'unique_named_entities': 0.2629016553067186,
                'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0, 'subjectivity': 0.4434417344173443,
                'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0, 'pronoun_3_perc': 0.0, 'direct_quotes': 5,
                'modal_adverbs_perc': 0.0, 'sentences': 97, 'adjectives_perc': 0.0, 'named_entities_perc': 0.632,
                'pronoun_1_perc': 0.0, 'pronoun_2_perc': 0.0, 'digits_perc': 0.004923076923076923,
                'intensifiers_perc': 0.0},
               {'polarity': 0.022609289617486348, 'avg_sentence_length': 15, 'question_marks_perc': 0.01079136690647482,
                'unique_named_entities': 0.38108882521489973, 'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0,
                'subjectivity': 0.6259562841530054, 'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0,
                'pronoun_3_perc': 0.0, 'direct_quotes': 12, 'modal_adverbs_perc': 0.0, 'sentences': 36,
                'adjectives_perc': 0.0, 'named_entities_perc': 0.6276978417266187, 'pronoun_1_perc': 0.0,
                'pronoun_2_perc': 0.0, 'digits_perc': 0.017985611510791366, 'intensifiers_perc': 0.0},
               {'polarity': 0.001024720893141945, 'avg_sentence_length': 17,
                'question_marks_perc': 0.0034334763948497852, 'unique_named_entities': 0.30171277997364954,
                'modal_verbs_perc': 0.0, 'exclamation_marks_perc': 0.0, 'subjectivity': 0.5608997873471558,
                'cogn_verbs_perc': 0.0, 'currency_symbols_perc': 0.0017167381974248926, 'pronoun_3_perc': 0.0,
                'direct_quotes': 10, 'modal_adverbs_perc': 0.0, 'sentences': 65, 'adjectives_perc': 0.0,
                'named_entities_perc': 0.6515021459227468, 'pronoun_1_perc': 0.0, 'pronoun_2_perc': 0.0,
                'digits_perc': 0.050643776824034335, 'intensifiers_perc': 0.0}]