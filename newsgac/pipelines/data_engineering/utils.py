#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Genre Classifier
#
# Copyright (C) 2016 Juliette Lonij, Koninklijke Bibliotheek -
# National Library of the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

genres = {
    -1: ['Unlabelled'],
    1: ['Nieuwsbericht'],
    2: ['Interview'],
    3: ['Reportage/feature'],
    4: ['Verslag'],
    5: ['Opiniestuk'],
    6: ['Recensie'],
    7: ['Achtergrond/Nieuwsanalyse'],
    8: ['Column'],
    9: ['Hoofdredactioneel commentaar'],
    10: ['Service'],
    11: ['Losse afbeelding'],
    12: ['Overzicht'],
    13: ['Ingezonden brief'],
    14: ['Fictie'],
    15: ['Essay'],
    16: ['Mededeling krant (rectificatie)'],
    17: ['Profiel/portret/necrologie'],
    18: ['Moppen/spreuken/puzzels/weetjes']

}

genres_labels = {
    'Unlabelled': -1,
    'Nieuwsbericht': 1,
    'Interview': 2,
    'Reportage/feature': 3,
    'Verslag': 4,
    'Opiniestuk': 5,
    'Recensie': 6,
    'Achtergrond': 7,
    'Column': 8,
    'HR commentaar': 9,
    'Service': 10,
    'Afbeelding': 11,
    'Overzicht': 12,
    'Brief': 13,
    'Fictie': 14,
    'Essay': 15,
    'Rectificatie': 16,
    'Profiel': 17,
    'Moppen': 18
}

genres_labels_inverse = {v: k for k, v in genres_labels.iteritems()}


genre_codebook = {
    'UNL' : -1,
    'NIE' : 1,
    'INT' : 2,
    'REP' : 3,
    'VER' : 4,
    'OPI' : 5,
    'REC' : 6,
    'ACH' : 7,
    'COL' : 8,
    'HOO' : 9,
    'SER' : 10,
    'LOS' : 11,
    'OVE' : 12,
    'ING' : 13,
    'FIC' : 14,
    'ESS' : 15,
    'MED' : 16,
    'PRO' : 17,
    'MOP' : 18
}


genre_codebook_friendly = { code: genres_labels_inverse[num] for code, num in genre_codebook.iteritems() }

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
    'Moeten', 'Moest',
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

