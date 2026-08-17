"""
Double Linked List example
"""

# Python Program for traversal of a doubly linked list
class Node:
    def __init__(self, data):
        # Initialize a new node with data, previous, and next pointers
        self.data = data
        self.next = None
        self.prev = None


def traverse(head):
    # Traverse the doubly linked list and print its elements
    current = head
    while current:
      # Print current node's data
        print(current.data, end=" <-> ")
        # Move to the next node
        current = current.next
    print("None")


def insert_at_beginning(head, data):
    # Insert a new node at the beginning of the doubly linked list
    new_node = Node(data)
    new_node.next = head
    if head:
        head.prev = new_node
    return new_node

def append(head, data):
    # Insert a new node at the end of the doubly linked list
    new_node = Node(data)
    if head is None:
        return new_node

    current = head
    while current.next:
        current = current.next

    current.next = new_node
    new_node.prev = current
    return head

def test02():
    head = None
    head = insert_at_beginning(head, 3)
    head = append(head, 4)
    head = append(head, 6)
    head = append(head, 8)
    head = insert_at_beginning(head, 3)

    traverse(head)
    
def test01():
    # Driver Code
    head = None
    head = insert_at_beginning(head, 4)
    head = insert_at_beginning(head, 3)
    head = insert_at_beginning(head, 2)
    head = insert_at_beginning(head, 1)

    # To traverse and print the nodes:
    traverse(head)


# test01()
test02()