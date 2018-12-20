from newsgac.nlp_tools import FrogTFIDF
from newsgac.nlp_tools.models.frog import Frog
from newsgac.nlp_tools.models.tfidf import TFIDF

tools = [Frog, TFIDF, FrogTFIDF]

def create_nlp_tool(tag, with_defaults=True, **kwargs):
    for tool in tools:
        if tool.tag == tag:
            if with_defaults:
                return tool.create(**kwargs)
            else:
                return tool(**kwargs)
    raise ValueError('No nlp tool with tag "%s"' % tag)
