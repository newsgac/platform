__author__ = 'abilgin'

COLLECTION = "data_sources_list"
COLLECTION_PROCESSED = "processed_data"
COLLECTION_REAL_PROCESSED = "real_processed_data"

NON_FEATURE_COLUMNS = ['_id', 'date', 'genre', 'genre_friendly', 'article_raw_text', 'article_processed_text', 'data_source_id']

DEFAULT_SW_REMOVAL = False
DEFAULT_LEMMA = False
DEFAULT_SCALING = False
DEFAULT_NLP_TOOL = "frog"
