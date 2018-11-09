feature_descriptions = {
    # 'pronoun_1' : 'The number of first person pronouns (e.g. ik, mij, me) within the text',
    'pronoun_1_perc' : 'The percentage of the occurrence of first person pronouns with regards to the total number of tokens after the removal of direct quotes',
    # 'pronoun_1_perc_rel': 'The percentage of the occurrence of first person pronouns with regards to the total number of pronouns (i.e. sum of first person, second person and third person pronouns) after the removal of direct quotes',
    # 'pronoun_2' : 'The number of second person pronouns (e.g. jij, jouw, jullie) within the text',
    'pronoun_2_perc' : 'The percentage of the occurrence of second person pronouns with regards to the total number of tokens after the removal of direct quotes',
    # 'pronoun_2_perc_rel' : 'The percentage of the occurrence of second person pronouns with regards to the total number of pronouns (i.e. sum of first person, second person and third person pronouns) after the removal of direct quotes',
    # 'pronoun_3' : 'The number of third person pronouns (e.g. hij, zijn, hun) within the text',
    'pronoun_3_perc' : 'The percentage of the occurrence of third person pronouns with regards to the total number of tokens after the removal of direct quotes',
    # 'pronoun_3_perc_rel' : 'The percentage of the occurrence of third person pronouns with regards to the total number of pronouns (i.e. sum of first person, second person and third person pronouns) after the removal of direct quotes',
    'number_perc' : 'The percentage of the occurrence of numbers with regards to the total number of tokens after the removal of direct quotes',
    # 'adjectives' : 'The number of adjectives in the Part-Of-Speech tagged sentences within the text after the removal of direct quotes',
    'adjectives_perc' : 'The percentage of the occurrence of adjectives with regards to the total number of tokens after the removal of direct quotes',
    # 'modal_verbs' : 'The number of modal verbs (e.g. behoeven, blijken, moeten, etc.) within the text after the removal of direct quotes',
    'modal_verbs_perc' : 'The percentage of the occurrence of modal verbs with regards to the total number of tokens after the removal of direct quotes',
    # 'modal_adverbs' : 'The number of modal adverbs (e.g. allicht, eigenlijk, gelukkig, etc.) within the text after the removal of direct quotes',
    'modal_adverbs_perc' : 'The percentage of the occurrence of modal adverbs with regards to the total number of tokens after the removal of direct quotes',
    # 'intensifiers' : 'The number of intensifiers (e.g. aanmerkelijk, bijna, echt, etc.) within the text after the removal of direct quotes',
    'intensifiers_perc' : 'The percentage of the occurrence of intensifiers with regards to the total number of tokens after the removal of direct quotes',
    # 'cogn_verbs' : 'The number of cognitive verbs (e.g. afleiden, bijna, echt, etc.) within the text after the removal of direct quotes',
    'cogn_verbs_perc' : 'The percentage of the occurrence of cognitive verbs with regards to the total number of tokens after the removal of direct quotes',
    # 'named_entities' : 'The number of named entitites (i.e. names in the text such as location, person, organization, product, etc.) within the text after the removal of direct quotes',
    'named_entities_perc' : 'The percentage of the occurrence of named entities with regards to the total number of tokens after the removal of direct quotes',
    # 'named_entities_pos' : 'The aggregated position of the named entities within the text calculated by taking the proportion of the normalized sum of indexes of the named entities to the total number of tokens after the removal of direct quotes',
    'unique_named_entities_perc' : 'The percentage of occurrence of unique named entities with regards to the total number of tokens after the removal of direct quotes',
    # 'self_cl_1' : 'Self classification bucket 1 includes genres of nieuwsbericht and nieuwsartikel',
    # 'self_cl_2' : 'Self classification bucket 2 includes genres of interview, tweegesprek, vraaggesprek and interviewen',
    # 'self_cl_3' : 'Self classification bucket 3 includes genres of reportage, sfeerverslag, ooggetuigeverslag, reconstructie and reisverslag',
    # 'self_cl_4' : 'Self classification bucket 4 includes verslag',
    # 'self_cl_5' : 'Self classification bucket 5 includes opiniestuk, commentaar, opinie, betoog, hoofdartikel and betogen',
    # 'self_cl_6' : 'Self classification bucket 6 includes recensie, boekbespreking, filmkritiek, theaterkritiek, filmbespreking and theaterbespreking',
    # 'self_cl_7' : 'Self classification bucket 7 includes nieuwsanalyse, analyse, achtergrond, achtergrondartikel and beschouwing',
    # 'self_cl_8' : 'Self classification bucket 8 includes column, cursiefje and rubriek',
    # 'self_cl_3-4' : 'Self classification bucket 3-4 includes verslag',
    # 'self_cl_3-8' : 'Self classification bucket 3-8 includes kroniek',
    # 'prevailing_tense' : 'The prevailing tense used in the document (-1:past, 0:equal, 1:present)',
    # manually added features
}
features = [
    # 'pronoun_1',
    'pronoun_1_perc',
    # 'pronoun_1_perc_rel',
    # 'pronoun_2',
    'pronoun_2_perc',
    # 'pronoun_2_perc_rel',
    # 'pronoun_3',
    'pronoun_3_perc',
    # 'pronoun_3_perc_rel',
    'number_perc',
    # 'adjectives',
    'adjectives_perc',
    # 'modal_verbs',
    'modal_verbs_perc',
    # 'modal_adverbs',
    'modal_adverbs_perc',
    # 'intensifiers',
    'intensifiers_perc',
    # 'cogn_verbs',
    'cogn_verbs_perc',
    # 'named_entities',
    'named_entities_perc',
    # 'named_entities_pos',
    'unique_named_entities_perc',
    # 'self_cl_1',
    # 'self_cl_2',
    # 'self_cl_3',
    # 'self_cl_4',
    # 'self_cl_5',
    # 'self_cl_6',
    # 'self_cl_7',
    # 'self_cl_8',
    # 'self_cl_3-4',
    # 'self_cl_3-8',
]