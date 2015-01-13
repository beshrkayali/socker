from collections import defaultdict
from functools import reduce


class Tree(defaultdict, dict):

    def __init__(self):
        defaultdict.__init__(self, self.__class__)
        self.members = set()

    def __repr__(self):
        repr_ = dict(self)
        repr_.update(self.__dict__)
        return repr(repr_)

    def walk(self, path):
        """
        Walk tree and yield tuple(key, node, is_leaf) in path.

        :param path: dot separated tree path
        """
        keys = iter(path.split('.'))
        key, node = None, self

        while node is not None:
            _key = next(keys, None)
            _node = node.get(_key)
            yield key, node, _key is None
            key, node = _key, _node

    def add(self, member, *paths):
        """
        Add member to tree at node paths.

        :param member: object to add in tree at paths
        :param paths: dot separated tree paths
        """
        for path in paths:
            leaf = reduce(lambda n, p: n[p], path.split('.'), self)
            leaf.members.add(member)

    def remove(self, member, *paths):
        """
        Remove member from tree at node paths.
        Cleanups affected nodes without members or siblings.

        :param member: object to add in tree at paths
        :param paths: dot separated tree paths
        """
        for path in paths:
            child = None
            nodes = list(self.walk(path))
            for name, node, is_leaf in reversed(nodes):
                if is_leaf:
                    node.members.remove(member)
                if child:
                    del node[child]
                if node.members or node.keys():
                    break
                child = name

    def get_members(self, path):
        """
        Get unique members for path, including parent wildcards.

        :param path: dot separated tree path
        :return: set of members
        """
        members = set()

        for _, node, is_leaf in self.walk(path):
            if is_leaf:
                members.update(node.members)
            elif '*' in node:
                members.update(node['*'].members)

        return members
