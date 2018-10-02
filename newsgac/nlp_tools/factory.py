from . import nlp_tools


def create_nlp_tool(tag, with_defaults=True, **kwargs):
    for tool in nlp_tools:
        if tool.tag == tag:
            if with_defaults:
                return tool.create(**kwargs)
            else:
                return tool(**kwargs)
    raise ValueError('No nlp tool with tag "%s"' % tag)
