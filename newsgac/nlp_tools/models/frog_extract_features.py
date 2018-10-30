#!/usr/bin/env python
# -*- coding: utf-8 -*-
import newsgac.data_engineering.utils as Utilities


def get_frog_features(tokens):
    features = {}

    # Token count
    token_count = len(tokens)

    # Numbers
    # num_count = len([t for t in tokens if t[4].startswith('TW')])
    # features['number_perc'] = (num_count / float(token_count)) if float(token_count) > 0 else 0

    # Adjective count and percentage
    adj_count = len([t for t in tokens if t[4].startswith('ADJ')])
    features['adjectives_perc'] = (adj_count / float(token_count)) if float(token_count) > 0 else 0

    # Verbs and adverbs count and percentage
    modal_verb = [t for t in tokens if t[4].startswith('WW') and
                  t[2].capitalize() in Utilities.modal_verbs]
    modal_verb_count = len(modal_verb)
    features['modal_verbs_perc'] = (modal_verb_count / float(token_count)) if float(token_count) > 0 else 0

    modal_adverb_count = len([t for t in tokens if t[4].startswith('BW')
                              and t[2].capitalize() in Utilities.modal_adverbs])
    features['modal_adverbs_perc'] = (modal_adverb_count /
                                      float(token_count)) if float(token_count) > 0 else 0

    cogn_verb_count = len([t for t in tokens if t[4].startswith('WW') and
                           t[2].capitalize() in Utilities.cogn_verbs])
    features['cogn_verbs_perc'] = (cogn_verb_count / float(token_count)) if float(token_count) > 0 else 0

    intensifier_count = len([t for t in tokens if t[2].capitalize() in
                             Utilities.intensifiers])
    features['intensifiers_perc'] = (intensifier_count / float(token_count)) if float(token_count) > 0 else 0

    # Personal pronoun counts and percentages
    pronoun_1_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_1])
    # pronoun_1_count_wdq = pronoun_1_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
    #                                             t[2] in Utilities.pronouns_1])
    pronoun_2_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_2])
    # pronoun_2_count_wdq = pronoun_2_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
    #                                              t[2] in Utilities.pronouns_2])
    pronoun_3_count = len([t for t in tokens if t[4].startswith('VNW') and
                           t[2] in Utilities.pronouns_3])

    features['pronoun_1_perc'] = (pronoun_1_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_2_perc'] = (pronoun_2_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_3_perc'] = (pronoun_3_count / float(token_count)) if float(token_count) > 0 else 0

    # features['pronoun_1_perc_wdq'] = (pronoun_1_count_wdq / float(token_count)) if float(token_count) > 0 else 0
    # features['pronoun_2_perc_wdq'] = (pronoun_2_count_wdq / float(token_count)) if float(token_count) > 0 else 0

    # Named entities
    named_entities = [t for t in tokens if t[5].startswith('B')]

    features['named_entities_perc'] = (len(named_entities) /
                                       float(token_count)) if float(token_count) > 0 else 0

    # Unique named entities
    unique_ne_strings = []
    ne_strings = set([t[1].lower() for t in named_entities])
    for ne_source in ne_strings:
        unique = True
        for ne_target in [n for n in ne_strings if n != ne_source]:
            if ne_target.find(ne_source) > -1:
                unique = False
                break
        if unique:
            unique_ne_strings.append(ne_source)

    features['unique_named_entities'] = (len(unique_ne_strings) /
                                         float(len(named_entities))) if len(named_entities) else 0
    return features
