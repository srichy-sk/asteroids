'''
An array can hold many values under a single name, and you can access
the values by referring to an index number. This is a special thing
about arrays
'''

import numpy

array1 = ["Toyota","Honda","Subaru","Tesla"]

x = array1[0]
print(x)
print(array1[0])

array1[3] = "Mercedes" # Note that tesla is gone
print(array1)

x = len(array1)
print(x)
print(len(array1))

for item in array1:
    print(item)

array1.append("Tesla") # Note that this doesn’t take away anything from the array
print(array1)

array1.pop(2) # Note that pop() uses the index
print(array1)

array1.remove("Mercedes") # Note that remove() uses the name, not the index
print(array1)

'''
Other array methods:

    Method    Description
    append()    Adds an element at the end of the list
    clear()        Removes all the elements from the list
    copy()        Returns a copy of the list
    count()        Returns the number of elements with the specified value
    extend()    Add the elements of a list (or any iterable), to the end of the current list
    index()        Returns the index of the first element with the specified value
    insert()    Adds an element at the specified position
    pop()        Removes the element at the specified position
    remove()    Removes the first item with the specified value
    reverse()    Reverses the order of the list
    sort()        Sorts the list

'''