#!/usr/bin/env python
# -*- coding: utf-8 -*-
genres_full = [
    'Nieuwsbericht',
    'Interview',
    'Reportage/feature',
    'Verslag',
    'Opiniestuk',
    'Recensie',
    'Achtergrond/Nieuwsanalyse',
    'Column',
    'Service',
    'Losse afbeelding',
    'Overzicht',
    'Ingezonden brief',
    'Fictie',
    'Essay',
    'Mededeling krant (rectificatie) / Moppen',
    'Portret',
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
    'Service',
    'Afbeelding',
    'Overzicht',
    'Brief',
    'Fictie',
    'Essay',
    'Mededeling',
    'Portret',
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
    'SER',
    'LOS',
    'OVE',
    'ING',
    'FIC',
    'ESS',
    'MED',
    'POR',
    'UNL',
]

if len(genre_codes) == len(genres_full) == len(genre_labels): raise AssertionError()

genre_unlabeled_index = len(genre_codes) - 1

