import re
import traceback


LIMIT_KEY_CHAR = '~'


def retry_on_exception(exception):
    print "Retried: {}".format(traceback.format_exc())
    return not isinstance(exception, KeyboardInterrupt)


def get_num_partitions(hsp, collection_name):
    """Gets number of partitions of a partitioned collection.
    Returns None if collection is not partitioned
    """
    partitions = []
    partitions_re = re.compile(r'%s_(\d+)' % collection_name)
    for entry in hsp.collections.apiget('list'):
        m = partitions_re.match(entry['name'])
        if m:
            partitions.append(int(m.groups()[0]))
    if partitions:
        if len(partitions) == max(partitions) + 1:
            return len(partitions)

def filter_collections_exist(hsp, collection_names):
    """
    Filters a list of collections to return only those that do exist
    """
    filtered = []
    for entry in hsp.collections.apiget('list'):
        if entry['name'] in collection_names:
            filtered.append(entry['name'])
    return filtered

def generate_prefixes(col, codelen, startafter=None, **kwargs):
    data = True
    # TODO: remove this once fix KUMO-1578 in hubstorage server is deployed
    col._collections._allows_mpack = lambda x: False
    while data:
        data = False
        for r in col.get(nodata=1, meta=['_key'], startafter=startafter, count=1, **kwargs):
            data = True
            code = r['_key'][:codelen]
            startafter = code + LIMIT_KEY_CHAR
            yield code

