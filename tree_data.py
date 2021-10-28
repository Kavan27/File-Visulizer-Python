"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2020 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""

from __future__ import annotations
import os
from random import randint
import math

from typing import Tuple, List, Optional


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    data_size: the total size of all leaves of this tree.
    colour: The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    _root: the root value of this tree, or None if this tree is empty.
    _subtrees: the subtrees of this tree.
    _parent_tree: the parent tree of this tree; i.e., the tree that contains
        this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    data_size: int
    colour: (int, int, int)
    _root: Optional[object]
    _subtrees: List[AbstractTree]
    _parent_tree: Optional[AbstractTree]

    def __init__(self: AbstractTree, root: Optional[object],
                 subtrees: List[AbstractTree], data_size: int = 0) -> None:
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None
        self.data_size = data_size
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        for subtree in self._subtrees:
            subtree._parent_tree = self
            self.data_size += subtree.data_size

    def is_empty(self: AbstractTree) -> bool:
        """Return True if this tree is empty."""
        return self._root is None

    def generate_treemap(self: AbstractTree, rect: Tuple[int, int, int, int]) \
            -> List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        x, y, width, height = rect
        last_width, last_height, main = x + width, y + height, []
        trees = (None, None, (None, None))
        if self.is_empty() or self.data_size == 0:
            return []
        elif len(self._subtrees) == 0:
            return [(rect, self.colour)]
        if width > height:
            for subtree in self._subtrees:
                u_width = math.floor(
                    (subtree.data_size / self.data_size) * width)
                temp = subtree.generate_treemap((x, y, u_width, height))
                main += temp
                if temp:
                    trees = (-len(temp), subtree, (x, y))
                if subtree == self._subtrees[-1]:
                    main, t = main[:trees[0]], trees[2][0]
                    main += trees[1].generate_treemap(
                        (t, y, last_width
                         - t, height))
                x += u_width
        else:
            for subtree in self._subtrees:
                u_height = math.floor(
                    (subtree.data_size / self.data_size) * height)
                temp = subtree.generate_treemap((x, y, width, u_height))
                main += temp
                if temp:
                    trees = (-len(temp), subtree, (x, y))
                if subtree == self._subtrees[-1]:
                    main, t = main[:trees[0]], trees[2][1]
                    main += trees[1].generate_treemap((x, t, width,
                                                       last_height - t))
                y += u_height
        return main

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.
        """
        raise NotImplementedError

    def remove_subtree(self, leaf: AbstractTree) -> None:
        """
        Removes the inputted <leaf> from the list of subtrees
        of self.
        """
        self._subtrees.remove(leaf)

    def check_pos(self, pos: Tuple[int, int],
                  rect: Tuple[int, int, int, int]) \
            -> Optional[AbstractTree]:
        """
        Takes a x, y <pos> of the user's mouse click and a tuple of the py game
        format <rect> and finds out which node was clicked and returns the
        node or None if nothing was clicked.
        """
        lst = self.generate_treemap(rect)
        x, y = pos
        leaves = self.find_leafs()
        c = 0
        flag = True
        for tup in lst:
            cords = tup[0]
            c += 1
            if cords[0] <= x <= (cords[2] + cords[0]) and \
                    cords[1] <= y <= (cords[3] + cords[1]):
                flag = False
                break
        if not leaves or flag:
            return None
        return leaves[c - 1]

    def find_leafs(self) -> [AbstractTree]:
        """
        returns a list of all the leaves in self.
        """
        if self.is_empty() or self.data_size == 0:
            return []
        elif not self._subtrees:
            return [self]
        else:
            main = []
            for subtree in self._subtrees:
                main += subtree.find_leafs()
        return main

    @staticmethod
    def get_path(leaf: AbstractTree) \
            -> str:
        """
        Returns the string representation of the path from the inputted abstract
        tree <leaf> and joins all the paths up till its parent trees.
        """
        main = ""
        token = leaf
        while token._parent_tree is not None:
            main = os.path.join(str(token._root), main)
            token = token._parent_tree
        main = os.path.join(str(token._root), main)
        return main[:-1]

    @staticmethod
    def delete_leaf(leaf: AbstractTree) -> None:
        """
        Deletes the inputted abstract tree <leaf> from the parent trees subtrees
        and changing the sizes of the parent trees and the leaf, finally setting
        the leaf's data size to 0.
        """
        leaf._parent_tree.remove_subtree(leaf)
        token = leaf
        while token._parent_tree is not None:
            token = token._parent_tree
            token.data_size -= leaf.data_size
        leaf._parent_tree = None
        leaf.data_size = 0

    @staticmethod
    def increase_leaf(leaf: AbstractTree) -> None:
        """
        Input is a abstract tree <leaf>, 1 % of the leafs data size is taken and
        added to the data size of leaf and added to the parents data sizes.
        """
        add_size = math.ceil(0.01 * leaf.data_size)
        leaf.data_size += add_size
        token = leaf
        while token._parent_tree is not None:
            token = token._parent_tree
            token.data_size += add_size

    @staticmethod
    def decrease_leaf(leaf: AbstractTree) -> None:
        """
        Input is a abstract tree <leaf>, 1 % of the leafs data size is taken and
        subtracted to the data size of leaf and subtracted from the parents
        data sizes and in the case where the value goes less than 1 it sets
        the data size to 1 and prevents it from going lower.
        """
        decrease_size = math.ceil(0.01 * leaf.data_size)
        if leaf.data_size - decrease_size < 1:
            decrease_size = abs(leaf.data_size - decrease_size)
            leaf.data_size = 1
        else:
            leaf.data_size -= decrease_size
        token = leaf
        while token._parent_tree is not None:
            token = token._parent_tree
            token.data_size -= decrease_size


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self: FileSystemTree, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        root = os.path.basename(path)
        subtree = []
        data_size = 0
        if os.path.isdir(path):
            for x in os.listdir(path):
                new_path = os.path.join(path, x)
                subtree.append(FileSystemTree(new_path))
        else:
            data_size = os.path.getsize(path)
        super().__init__(root, subtree, data_size)

    def get_separator(self: FileSystemTree) -> None:
        raise NotImplementedError


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'extra-imports': ['os', 'random', 'math'],
            'generated-members': 'pygame.*'})
