#!/usr/bin/env python
# -*- coding: utf-8 -*-
pronouns_1 = [
    'ik',
    'mij',
    'me',
    'mijn',
    'wij',
    'we',
    'ons'
]

pronouns_2 = [
    'jij',
    'je',
    'jou',
    'jouw',
    'jullie',
    'u',
    'uw'
]

pronouns_3 = [
    'hij',
    'hem',
    'zij',
    'ze',
    'zijn',
    'haar',
    'hun',
    'hen',
    'zich'
]

modal_verbs = [
    'Behoeven',
    'Blijken',
    'Dunken',
    'Heten',
    'Hoeven',
    'Lijken',
    'Kunnen',
    'Moeten',
    'Moest',
    'Mogen',
    'Schijnen',
    'Toeschijnen',
    'Voorkomen',
    'Willen',
    'Zullen'
]

modal_adverbs = [
    'Allicht',
    'Blijkbaar',
    'Eigenlijk',
    'Gelukkig',
    'Godweet',
    'Helaas',
    'Hoofdzakelijk',
    'Hoogstwaarschijnlijk',
    'Hopelijk',
    'Jammer',
    'Kennelijk',
    'Misschien',
    'Mogelijk',
    'Natuurlijk',
    'Ongelukkigerwijs',
    'Ongetwijfeld',
    'Onmogelijk',
    'Onwaarschijnlijk',
    'Schijnbaar',
    'Stellig',
    'Tevergeefs',
    'Trouwens',
    'Tuurlijk',
    'Uiteraard',
    'Vergeefs',
    'Vermoedelijk',
    'Waarlijk',
    'Waarschijnlijk',
    'Wellicht',
    'Wieweet',
    'Zeker',
    'Zogenaamd',
    'Zonder twijfel'
]

intensifiers = [
    'Aanmerkelijk',
    'Aanzienlijk',
    'Bijna',
    'Behoorlijk',
    'Drastisch',
    'Echt',
    'Enigszins',
    'Enorm',
    'Erg',
    'Extra',
    'Flink',
    'Gewoon',
    'Godsgruwelijk',
    'Hartstikke',
    'Helemaal',
    'Hoezeer',
    'Nagenoeg',
    'Nauwelijks',
    'Nogal',
    'Oneindig',
    'Ongemeen',
    'Ongeveer',
    'Ontzettend',
    'Onuitsprekelijk',
    'Onwijs',
    'Pakweg',
    'Uitdrukkelijk',
    'Uitermate',
    'Uitsluitend',
    'Voldoende',
    'Volkomen',
    'Volledig',
    'Vooral',
    'Voornamelijk',
    'Vreselijk',
    'Vrijwel',
    'Welhaast',
    'Zo',
    'Zoveel',
    'Zowat'
]

cogn_verbs = [
    'Aankondigen',
    'Aarzelen',
    'Aannemen',
    'Achten',
    'Afwijzen',
    'Afleiden',
    'Bedenken',
    'Bedoelen',
    'Begrijpen',
    'Bekennen',
    'Beloven',
    'Beslissen',
    'Betreuren',
    'Betwijfelen',
    'Concluderen',
    'Denken',
    'Dreigen',
    'Geloven',
    'Herinneren',
    'Herkennen',
    'Hopen',
    'Menen',
    'Opmerken',
    'Prefereren',
    'Reageren',
    'Realiseren',
    'Suggereren',
    'Uitleggen',
    'Uitsluiten',
    'Uitvinden',
    'Vaststellen',
    'Verdenken',
    'Vergeten',
    'Verlangen',
    'Vermoeden',
    'Vernemen',
    'Veronderstellen',
    'Vertrouwen',
    'Verwachten',
    'Vinden',
    'Voelen',
    'Voorstellen',
    'Vragen',
    'Vrezen',
    'Waarschuwen',
    'Wensen',
    'Weten'
]



def get_frog_features(tokens):
    features = {}

    # Token count
    token_count = len(tokens)

    # Numbers
    num_count = len([t for t in tokens if t[3].startswith('TW')])
    features['number_perc'] = (num_count / float(token_count)) if float(token_count) > 0 else 0

    # Adjective count and percentage
    adj_count = len([t for t in tokens if t[3].startswith('ADJ')])
    features['adjectives_perc'] = (adj_count / float(token_count)) if float(token_count) > 0 else 0

    # Verbs and adverbs count and percentage
    modal_verb = [t for t in tokens if t[3].startswith('WW') and
                  t[1].capitalize() in modal_verbs]
    modal_verb_count = len(modal_verb)
    features['modal_verbs_perc'] = (modal_verb_count / float(token_count)) if float(token_count) > 0 else 0

    modal_adverb_count = len([t for t in tokens if t[3].startswith('BW')
                              and t[1].capitalize() in modal_adverbs])
    features['modal_adverbs_perc'] = (modal_adverb_count /
                                      float(token_count)) if float(token_count) > 0 else 0

    cogn_verb_count = len([t for t in tokens if t[3].startswith('WW') and
                           t[1].capitalize() in cogn_verbs])
    features['cogn_verbs_perc'] = (cogn_verb_count / float(token_count)) if float(token_count) > 0 else 0

    intensifier_count = len([t for t in tokens if t[1].capitalize() in
                             intensifiers])
    features['intensifiers_perc'] = (intensifier_count / float(token_count)) if float(token_count) > 0 else 0

    # Personal pronoun counts and percentages
    pronoun_1_count = len([t for t in tokens if t[3].startswith('VNW') and
                           t[1] in pronouns_1])
    # pronoun_1_count_wdq = pronoun_1_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
    #                                             t[2] in Utilities.pronouns_1])
    pronoun_2_count = len([t for t in tokens if t[3].startswith('VNW') and
                           t[1] in pronouns_2])
    # pronoun_2_count_wdq = pronoun_2_count + len([t for t in quote_tokens if t[4].startswith('VNW') and
    #                                              t[2] in Utilities.pronouns_2])
    pronoun_3_count = len([t for t in tokens if t[3].startswith('VNW') and
                           t[1] in pronouns_3])

    features['pronoun_1_perc'] = (pronoun_1_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_2_perc'] = (pronoun_2_count / float(token_count)) if float(token_count) > 0 else 0
    features['pronoun_3_perc'] = (pronoun_3_count / float(token_count)) if float(token_count) > 0 else 0

    # features['pronoun_1_perc_wdq'] = (pronoun_1_count_wdq / float(token_count)) if float(token_count) > 0 else 0
    # features['pronoun_2_perc_wdq'] = (pronoun_2_count_wdq / float(token_count)) if float(token_count) > 0 else 0

    # Named entities
    named_entities = [t for t in tokens if t[4].startswith('B')]

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
