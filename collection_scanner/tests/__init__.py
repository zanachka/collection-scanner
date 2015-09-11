"""
utils for mocking hubstorage collection
"""
from operator import itemgetter
from copy import deepcopy

from mock import patch

class FakeCollection(object):
    def __init__(self, samples):
        """
        samples is a list of tuples (key, record dict)
        """
        self.samples = sorted(samples, key=itemgetter(0))
        self.base_time = 1442003291000
    
    @staticmethod
    def _must_issue_record(key, **kwargs):
        prefixes = kwargs.get('prefix')
        retval = prefixes is None
        if not retval:
            for prefix in prefixes:
                if key.startswith(prefix):
                    retval = True
                    break
        startafter = kwargs.get('startafter') or ''
        if isinstance(startafter, list):
            startafter = startafter[0]
        retval = retval and key > startafter
        return retval


    def get(self, **kwargs):
        include_key = '_key' in kwargs.get('meta', {})
        include_ts = '_ts' in kwargs.get('meta', {})
        count = kwargs.get('count') or None
        if isinstance(count, list):
            count = count[0]
        for key, value in self.samples[:count]:
            rvalue = deepcopy(value)
            if self._must_issue_record(key, **kwargs):
                if include_key:
                    rvalue['_key'] = key
                if include_ts:
                    rvalue['_ts'] = self.base_time
                    self.base_time += 10
                yield rvalue

class FakeCollections(object):
    def __init__(self, project):
        self.project = project

    def new_store(self, name):
        return FakeCollection(self.project.client.samples[name])

class FakeProject(object):
    def __init__(self, client):
        self.client = client
        self.collections = FakeCollections(self)

class FakeClient(object):
    def __init__(self, samples):
        self.samples = samples

    def get_project(self, *args):
        return FakeProject(self)
