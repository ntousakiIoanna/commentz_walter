#!/sr/bin/env python3
# -*- coding: utf-8 -*-

"""Commentz-Walter algorithm implementation"""

__author__ = 'Ioanna Ntousaki'
__version__ = '3.10.11'

from sys import argv
from collections import deque
import argparse


parser = argparse.ArgumentParser(description="Search keywords in a file.")
parser.add_argument("kw", nargs="+", help="One or more keywords to search.")
parser.add_argument("input_filename", help="Name of the input file.")
parser.add_argument("-v", action="store_true", help="Show additional output: value s1 & s2 .")
args = parser.parse_args()


# Reverse a string 
def reverseString(string):
    string = string[::-1].strip()
    return string

# Take a strings table and find the word with the maximum length 
def findMaxWord(givenWords):
    maxWord = givenWords[0]
    maxLength = len(givenWords[0])
    for word in givenWords[1:]:
        if len(word) > maxLength:
            maxWord = word
            maxLength = len(word)
    return maxWord

# Find the minimum word-length in the table 
def findMinLength(maxWord, givenWords):
    pmin = len(maxWord)
    for word in givenWords:
        if len(word) < pmin:
            pmin = len(word)
    return pmin

# Create a prefix trie from table of strings
def createTrie(maxWord, givenWords):
    
    # Initialize trie
    trie = {}
    trie[0] = []

    # Add the maximum word into the trie
    node = 0 
    for char in maxWord :   # For each character, add a new node into the trie and associate him with the next node-character
        trie[node].append([node + 1, char])
        node += 1
        trie[node] = []

    # Add all the words except maxWord into the trie
    for word in givenWords:
        if word != maxWord: # Check that the word processing is not the maxWord
            node = 0
            stopMatching = False    # Termination Condition : the registration of the word in the trie has completed as soon as stopMatching turns true
            for char in range(len(word)):   # Try to match each character into a node in trie
                    for adjNode in trie[node]:
                        
                        # If there is a match, move to the next character
                        if adjNode[1] == word[char]:    
                            node = adjNode[0]
                            break
                        
                        # Have checked the last adjacent node and the char has not matched with any edge
                        elif adjNode == trie[node][-1]: 
                            
                            # Add a new node with the character checked perceived 
                            # as an edge for (u,v) where u the last node checked and v the new node added
                            newNode = len(trie)
                            trie[newNode] = []
                            trie[node].append([newNode, word[char]])
                            
                            # Create a node for each character remained in the word and associate them (create a new path)
                            for character in word[char + 1:]:
                                newNode +=1
                                trie[newNode] = []
                                trie[newNode - 1].append([newNode, character])
                            # All characters have been settled in the trie, so stop checking the adjacent nodes to match characters
                            stopMatching = True
                            break
                    # The word has been fully settled in the trie, so stop checking for any other character
                    if stopMatching == True:
                        break

    return trie

# Create failure table    
def createFailureTable(trie, depth, parent):
    failure = [0] * len(trie)
    queue = deque()

    # Initialize the queue with the child nodes of the root node 0
    for adjNode in trie[0]:
        
        # Keep the depth of the node
        depth[adjNode[0]] = 1
        
        # Store the parent of the node 
        parent[adjNode[0]] = 0
        
        # Insert the node into the queue to start bfs
        queue.append(adjNode[0])
        
        # Insert into the rightest appearances table the characters of the nodes in depth 1
        # We are sure that these characters are unique so we insert them all
        rt[adjNode[1]] = 1 

    while not (len(queue) == 0):
        u = queue.popleft()
        # Traverse the edges of the root node
        for adjNode in trie[u]:
            
            # Calculate depth of adjacent nodes - depth is equal to its parent's depth + 1
            depth[adjNode[0]] = depth[u] + 1
            
            # Keep the node's parent - parent is the node extracted from the queue
            parent[adjNode[0]] = u
            
            queue.append(adjNode[0])
            
            u_prime = failure[u]
            
            if not adjNode[1] in rt:
                rt[adjNode[1]] = depth[adjNode[0]]
            
            # Find the deepest node with a matching edge
            while u_prime != 0 and adjNode[1] not in [edge[1] for edge in trie[u_prime]]:
                u_prime = failure[u_prime]

            # Update the failure value for the current node
            if adjNode[1] in [edge[1] for edge in trie[u_prime]]:
                # Find the matching edge and retrieve the corresponding node index
                for edge in trie[u_prime]:
                    if edge[1] == adjNode[1]:
                        failure[adjNode[0]] = edge[0]
                        break
            else:
                # No matching edge found, set failure value to 0
                failure[adjNode[0]] = 0

    # Return the failure table and the updated depth and parent tables
    return failure, depth, parent


# Create set1 : set1[𝑢] = {𝑣 ∶ failure[𝑣] = 𝑢}
def createTableSet1(failure):
    set1 = {}

    for u in range(len(failure)):
        if failure[u] != 0 :
            if failure[u] not in set1:
                set1[failure[u]] = []
            set1[failure[u]].append(u)
    return set1



# Create set2: set2[𝑢] = {𝑣 ∶ 𝑣 ∈ set1[𝑢] & 𝑣 terminal node in trie}
def createTableSet2(failure):
    set2 = {} 
    for i in set1:
        for j in set1[i]:
            if not trie[j]:
                if i not in set2:
                    set2[i] = []
                set2[i].append(j)
    return set2


# Create table s1
def createtableS1(trie, set1, pmin, depth):
    
    s1 = [1 for j in range(len(trie))]
    for node in range(len(trie)):
        if node != 0:
            if node not in set1:
                s1[node] = pmin
            else:
                s1[node] = min(pmin, min([depth[i] - depth[node] for i in set1[node]]))
    return s1

# Create table s2
def createtableS2(trie, set2, depth, parent):
    s2 = [pmin for j in range(len(trie))]
    for node in range(1,len(trie)):
            if node not in set2:
                s2[node] = s2[parent[node]]
            else:
                s2[node] = min(s2[parent[node]], min([depth[i] - depth[node] for i in set2[node]]))
    return s2



# Return if a node is connected with a child through an edge equal to the character given
def hasChild(trie, node, character):
    # Check all node's children and keep in a table the one that is connected with an edge equal to the character given
    match = [child for child in trie[node] if child[1] == character]
    
    # If there is a child that matches return true, else return false 
    if match:
        return True
    else:
        return False
    
# Return a node's child with witch its connected through the given character
def getChild(trie, node, character):
    
    return [child[0] for child in trie[node] if child[1] == character][0]

# Search inside a text for patterns that are given with the form of a trie
# Implement Commentz-Walter Algirithm
def findPatternsInText(pmin, trie, text, s1, s2, rt):
    q = deque()
    i = pmin - 1
    j = 0
    u = 0
    m = ''
    while i < len(text):
        while hasChild(trie, u, text[i - j]):
            u = getChild(trie, u, text[i - j])
            m = m + text[i - j]
            j = j + 1
            if not trie[u]: 
                q.append([reverseString(m), i - j + 1])
        if j > i :
            j = i
        s = min(s2[u], max(s1[u], rt[text[i - j]] - j - 1))
        i = i + s
        j = 0
        u = 0
        m = ''
    return q      


if __name__ == '__main__':
    
    # Insert the search keywords into a list
    givenWords = args.kw
    
    # Read the given file and insert the content into a string variable 
    with open(args.input_filename, 'r') as file:
        text = file.read().strip()
        
    # Reverse the search keywords 
    givenWords = [reverseString(word) for word in givenWords]
    
    # Find the string/word with the maximum length, to begin with
    maxWord = findMaxWord(givenWords)
    
    # Find the string/word with the minimum length
    pmin = findMinLength(maxWord, givenWords)
    
    # Create the prefix trie
    trie = createTrie(maxWord, givenWords)
    
    # Create dictionary rt[] with the rightest appearances of the characters according to the tree
    rt = {}
    
    # Create a table depth[] containing the depth of each node
    depth = [0 for i in range(len(trie))]
    
    # Create parent[] table containing the parent of each node 
    parent = [-1 for i in range(len(trie))]
    
    failure, depth, parent = createFailureTable(trie, depth, parent)
    
    set1 = createTableSet1(failure)
    set2 = createTableSet2(failure)

    s1 = createtableS1(trie, set1, pmin, depth) 
    s2 = createtableS2(trie, set2, depth, parent)
    
    # Number of unique chars in all the patterns + 1
    u_chars = len(rt) + 1
    # For each letter in the given text, except those that belong to the keywords too, 
    # add it to the dictionary rt with value equal to the unique characters number + 1
    for letter in text:
        if letter not in rt:
            rt[letter] = u_chars
            
    # If argument -v is given, print content of s1, s2
    if args.v :
        for node in trie:
            print(f"{node}: {s1[node]},{s2[node]}")
    # Print the patterns found in the text with the position of the pattern in it 
    for pattern in findPatternsInText(pmin, trie, text, s1, s2, rt):
        print(f"{pattern[0]}: {pattern[1]}")
            