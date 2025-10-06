"""
This module provides various functions to perform diff and merging
Functions:
    compare_snaps(s1, s2, path="."):
        Gets the overall comparison of files in snap1 and snap2.
    diff(f, t):
        Prints the changes when going from commit f to commit t.
    merge_snaps(f, t):
        Merge commit f_o_id to commit t_o_id.
    merge_blobs(branch, head):
        Merges two files. If conflicts arise, then will be indicated.
"""


from . import base
from . import data
import difflib
import os
from collections import defaultdict


def compare_snaps(s1, s2, path = "."):
    '''
    Gets the overall comparison of files in snap1 and snap2.\n
    Returns {filename : {0: oid1, 1: oid2}}.
    '''
    objects = defaultdict(lambda: [None, None])
    snaps = defaultdict(lambda: [None, None])

    for i, s in enumerate([s1, s2]):
        snap = data.get_object(s, expected='snap').decode().split("\n")
        for obj in snap[:-1]:
            o = obj.split(" ", 2)
            type = o[0]
            o_id = o[1]
            if type == 'snap':
                sub_path = f"{path}\{o[2]}"
                snaps[sub_path][i] = o_id
                sub_objects, sub_snaps = compare_snaps(o_id, o_id, sub_path)

                for sub_name, sub_obj in sub_objects.items():
                    objects[sub_name][i] = sub_obj[i]
                for sub_name, sub_snap in sub_snaps.items():
                    objects[sub_snap][i] = sub_obj[i]
                continue

            name = f"{path}\{o[2]}"
            objects[name][i] = o_id
        
    return objects, snaps

def diff(f, t):
    '''
    Prints the changes when going from commit f to commit t.
    '''
    f = base.get_commit(f)
    t = base.get_commit(t)
    files, snaps = compare_snaps(f.snap, t.snap)

    for filename, o_ids in files.items():
        print(filename)
        if o_ids[0] == o_ids[1]: continue
        elif o_ids[0] and not o_ids[1]:
            print(f"{filename} was deleted!")
        elif not o_ids[0] and o_ids[1]:
            print(f"{filename} was created!")
        else:
            # this means the file was modified
            print("Changes in", filename)
            file1 = data.get_object(o_ids[0], expected='blob').decode().split("\r")
            file2 = data.get_object(o_ids[1], expected='blob').decode().split("\r")
            d = difflib.unified_diff(file1, file2, lineterm='')
        
            for line in d:
                print(line)
        print()

    for snap, o_ids in snaps.items():
        # print(snap)
        if o_ids[0] and not o_ids[1]:
            print(f"{snap} was deleted!")
        elif not o_ids[0] and o_ids[1]:
            print(f"{snap} was created!")
        print()
    
    # just in case
    return files


def merge_snaps(f, t):
    '''
    Merge commit other snapshot to head snapshot.\n
    It will update the current snapshot to merged snapshot.\n
    Parameters: branch, head
    '''

    files, snaps = compare_snaps(f, t)
    
    # writing the merged to current snapshot and creating a new one and committing it.
    for snap, o_ids in snaps.items():
        # print(filename)
        if o_ids[0] and not o_ids[1]:
            os.makedirs(snap, exist_ok=True)
            print(f"{snap} was created!")
        elif not o_ids[0] and o_ids[1]:
            if os.path.exists(snap):
                os.rmdir(snap)
                print(f"{snap} was deleted!")

    for filename, o_ids in files.items():
        print(filename)
        if o_ids[0] and o_ids[1]:
            merged = merge_blobs(o_ids[0], o_ids[1])
            print(merged)
            with open(filename, 'w') as f:
                f.write("\n".join(merged))
        elif o_ids[0]:
            print("created")
            with open(filename, 'w') as f:
                f.write(data.get_object(o_ids[0], expected='blob').decode())

        elif o_ids[1]:
            print("deleted")
            os.remove(filename)
        print()


def merge_blobs(branch, head):
    '''
    Merges two files. If conflicts arises, then will be indicated.\n
    Returns the merged file.
    '''
    branch = data.get_object(branch, expected='blob').decode().split("\r")
    head = data.get_object(head, expected='blob').decode().split("\r")

    diff = difflib.ndiff(head, branch)
    
    flag1 = True
    flag2 = True
    output = []
    conflict_occur = False

    for d in diff:
        if d.startswith('-'):   # conflict started
            if flag1:
                conflict_occur = True
                output.append("<<<<<<< HEAD")
                flag1 = False
            output.append(d[2:])

        elif d.startswith('+'):
            if flag1 == False:   # if flag1 is false then it has entered the conflict block
                if flag2:   # if flag2 is true then we are just starting out with the second part of conflict block
                    output.append("=======")
                    flag2 = False
            output.append(d[2:])

        else:
            if flag1 == False:  # if the flag1 is false then we are still in confliuct block
                if flag2:       # if the flag2 is True then we have not started the branch's conflict block
                    output.append("=======")
                output.append(">>>>>>> branch")
                flag1 = True
                flag2 = True
                # we have ended the conflict block here
            output.append(d[2:])
    # just in case if there are no items in the list, we need to close the conflict
    if flag1 == False:
        if flag2:
            output.append("=======")
        output.append(">>>>>>> branch")
        flag1 = True
        flag2 = True

    if conflict_occur: print("Conflict Occured!")
    return output
