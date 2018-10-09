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

genres = [
    'Nieuwsbericht',
    'Interview',
    'Reportage/feature',
    'Verslag',
    'Opiniestuk',
    'Recensie',
    'Achtergrond/Nieuwsanalyse',
    'Column',
    'Hoofdredactioneel commentaar',
    'Service',
    'Losse afbeelding',
    'Overzicht',
    'Ingezonden brief',
    'Fictie',
    'Essay',
    'Mededeling krant (rectificatie)',
    'Profiel/portret/necrologie',
    'Moppen/spreuken/puzzels/weetjes',
    'Unlabelled',
]

genre_labels = [
    'Nieuwsbericht',
    'Interview',
    'Reportage/feature',
    'Verslag',
    'Opiniestuk',
    'Recensie',
    'Achtergrond',
    'Column',
    'HR commentaar',
    'Service',
    'Afbeelding',
    'Overzicht',
    'Brief',
    'Fictie',
    'Essay',
    'Rectificatie',
    'Profiel',
    'Moppen',
    'Unlabelled',
]

genre_codes = [
    'NIE',
    'INT',
    'REP',
    'VER',
    'OPI',
    'REC',
    'ACH',
    'COL',
    'HOO',
    'SER',
    'LOS',
    'OVE',
    'ING',
    'FIC',
    'ESS',
    'MED',
    'PRO',
    'MOP',
    'UNL',
]

genre_code_unlabeled = 'UNL'

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

