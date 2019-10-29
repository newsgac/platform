from newsgac.data_sources.parsers.csv import CSVParser
from newsgac.data_sources.parsers.newsgac import NewsgacFormatParser


def get_parser(format):
    if format == 'csv':
        return CSVParser
    elif format == 'newsgac':
        return NewsgacFormatParser
