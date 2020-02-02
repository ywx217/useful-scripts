#!/usr/bin/env python3
# remove empty directories
import os
import argparse
import shutil
from typing import NamedTuple, Dict, List


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', '-d', action='store_true', help='dry run')
    return p.parse_args()


class TreeNode(NamedTuple):
    parent: 'TreeNode'
    name: str
    mutable_vars: List
    children: Dict[str, 'TreeNode']

    @classmethod
    def create(cls, name:str, parent=None):
        return cls(parent, name, [True], {})

    @property
    def is_empty(self):
        return self.mutable_vars[0]
    
    @is_empty.setter
    def is_empty(self, b):
        self.mutable_vars[0] = b

    def find(self, path, *paths):
        """查找节点"""
        if not paths:
            paths = path.split('/')
        if paths and paths[0] == '.':
            paths = paths[1:]
        node = self
        for p in paths:
            if p not in node.children:
                return None
            node = node.children[p]
        return node

    def touch(self):
        """有文件的时候调用，标记自己和所有父节点is_empty=True"""
        node = self
        while node and node.is_empty:
            node.is_empty = False
            node = node.parent

    def on_walk(self, dirs, files):
        for d in dirs:
            self.children[d] = TreeNode.create(d, self)
        if files:
            self.touch()

    def get_path(self):
        paths = []
        n = self
        while n:
            paths.append(n.name)
            n = n.parent
        return '/'.join(reversed(paths))

    def visit_nodes(self, recurse_pred=lambda n: True):
        yield self
        if not recurse_pred(self):
            return
        for node in self.children.values():
            for n in node.visit_nodes(recurse_pred):
                yield n


def find_empty():
    # 构建目录树，默认节点都是False
    tree = TreeNode.create('.')
    for root, dirs, files in os.walk('.'):
        tree.find(root).on_walk(dirs, files)
    return [n for n in tree.visit_nodes(lambda n: not n.is_empty) if n.is_empty]


if __name__ == '__main__':
    args = parse_args()
    dirs = find_empty()
    if args.dry_run:
        for d in dirs:
            print(d.get_path())
        exit(0)
    for d in dirs:
        shutil.rmtree(d.get_path())
