"""
Learning binary search trees
"""


class TreeNode:
    idv = 0
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.id = TreeNode.idv
        TreeNode.idv += 1

    def __str__(self):
        return f"N[{self.id}]: {self.value}"

class BSTree:
    def __init__(self):
        self.root = None

    def findNodeByValue(self, target):
        if self.root == None:
            return None
        return FindValue(self.root, target)
    def InsertNode(self, newval):
        if self.root == None:
            self.root = TreeNode(newval)
        else:
            InsertNode(self.root, newval)


def InsertNode(current, newval):
    if current.value == newval:
        return current
    if newval < current.value:
        if current.left != None:
            InsertNode (current.left, newval)
        else:
            current.left = TreeNode(newval)
            current.left.parent = current
    else:
        if current.right != None:
            InsertNode(current.right, newval)
        else:
            current.right = TreeNode(newval)
            current.right.parent = current

def FindValue(root, target):
    current = root
    while current != None and current.value != target:
        if target < current.value:
            current = current.left
        else:
            current = current.right
    return current


def test03():
    bst = BSTree()
    datset = [40, 20, 30, 11, 56, 2]
    for d in datset:
        bst.InsertNode(d)
    
    an = bst.findNodeByValue(11)
    if an != None: print (an)


def test02():
    start = TreeNode(5)
    ln = TreeNode(2)
    rn = TreeNode(7)
    start.left = ln
    start.right = rn
    ln.parent = start
    rn.parent = start
    bst = BSTree()
    bst.root = start

    an = bst.findNodeByValue(7)
    if an != None: print (an)

    

def manual01():
    start = TreeNode(5)
    ln = TreeNode(2)
    rn = TreeNode(7)
    start.left = ln
    start.right = rn
    ln.parent = start
    rn.parent = start

    f = FindValue(start, 2)
    if f != None:
        print (f)
    else:
        print ("Failed FindValue()")

def main():
    # manual01()
    test03()

if __name__ == "__main__":
    main()
        