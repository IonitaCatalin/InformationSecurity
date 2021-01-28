# IS-HW1

General usage
  For this program to work we will need all the python file .py running node_A.py node_B.py key_manage.py
 ,key_manager.py - its primarily function is to take care of generating keys and ivs for the node which connects to it also to refresh a certain key when it is asked
 ,node_B.py - its primarily function is to decrypt any block of data encrypted in a certain way(CBC or OFB).Thsi node will react only when another node(which in our case is node_A will push data to it)
 ,node_A.py - it is our driver program,its main function it is to push encrypted data to node_B and to ask keys and iv from node key_manager
  
  Mentions:
    Parameters such as K3,what is the location of the file to be encrypted as well as where is the location of the file to be decrypted will be specified in the globals.py file
