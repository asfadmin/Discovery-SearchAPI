from lxml import etree

def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context

def serialize(elem):
    return elem.findtext('GranuleUR')

doc = etree.iterparse('test.xml', events=('end',), tag='Granule')

fast_iter(doc,
          lambda elem:
            print(serialize(elem)))
