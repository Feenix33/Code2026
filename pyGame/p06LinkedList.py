"""
Data Structures the Fun Way
Ch 3

Code from Geeks for Geeks
"""

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


def insertLink(head, value):
    if head == None:
        aNode = Node(value)
    else:
        aNode = head
        while aNode.next != None:
            aNode = aNode.next
        aNode.next = Node(value)
    return aNode

def printList(head):
    current = head
    while current:
        print(current.data, end=" -> ")
        current = current.next
    print("None")

# Create nodes
node1 = Node(15)
node2 = Node(3)
node3 = Node(17)
node4 = Node(90)

# Link nodes
node1.next = node2
node2.next = node3
node3.next = node4  

head = node1  # Head points to the first node

# Traverse and print the linked list
current = head
while current:
    print(current.data, end=" -> ")
    current = current.next
print("None")
printList(head)

bravo = None
bravo = insertLink (bravo, 5)
bravo = insertLink (bravo, 10)
bravo = insertLink (bravo, 15)
printList(bravo)


# class Node:
#     """Represents a single node in a singly linked list."""
#     def __init__(self, data):
#         self.data = data
#         self.next = None  # Pointer to the next node


class LinkedList:
    """Represents the linked list structure."""
    def __init__(self):
        self.head = None  # First node in the list

    def add(self, data):
        """Insert at beginning of list"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        return
    
    def insert(self, index, data):
        """Inserts a new node with data at a specific index."""
        new_node = Node(data)

        # Case 1: Insert at the beginning (index 0)
        if index == 0:
            new_node.next = self.head
            self.head = new_node
            return

        # Case 2: Insert at any position after the head
        current = self.head
        position = 0

        # Traverse to find the node right before the insertion index
        while current is not None and position < index - 1:
            current = current.next
            position += 1

        # If index is out of bounds (greater than the list length)
        if current is None:
            raise IndexError("Index out of bounds")

        # Adjust the pointers to insert the new node
        new_node.next = current.next
        current.next = new_node

    def display(self):
        """Helper method to print the linked list structure."""
        print ("ll.display ", end="")
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        print(" -> ".join(elements) + " -> None")


# --- Example Usage ---
ll = LinkedList()

# 1. Insert at index 0 (Empty list)
ll.insert(0, 10)  # List: 10 -> None

# 2. Insert at index 1 (End of list)
ll.insert(1, 30)  # List: 10 -> 30 -> None

# 3. Insert at index 1 (Middle of list)
ll.insert(1, 20)  # List: 10 -> 20 -> 30 -> None

# 4. Insert at the new front
ll.insert(0, 5)   # List: 5 -> 10 -> 20 -> 30 -> None

# Display final list
ll.display()

delta = LinkedList()
for _ in range(7):
    delta.add(_)
delta.display()
