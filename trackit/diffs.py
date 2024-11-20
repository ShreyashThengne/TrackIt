from . import base
from . import data
import difflib
import os

def compare_snaps(s1, s2, path = "."):
    '''
    Gets the overall comparison of files in snap1 and snap2.\n
    Returns {filename : {0: oid1, 1: oid2}}.
    '''
    objects = {}
    for i, s in enumerate([s1, s2]):
        snap = data.get_object(s, expected='tree').decode().split("\n")
        for obj in snap[:-1]:
            o = obj.split(" ", 2)
            type = o[0]

            o_id = o[1]
            if type == 'tree':
                sub_path = f"{path}\{o[2]}"
                sub_objects = compare_snaps(o_id, o_id, sub_path)

                for sub_name, sub_obj in sub_objects.items():
                    if objects.get(sub_name):
                        objects[sub_name][i] = sub_obj[i]
                    else:
                        objects[sub_name] = sub_obj
                        if i == 0:
                            objects[sub_name][1] = None
                        else:
                            objects[sub_name][0] = None
                continue

            name = f"{path}\{o[2]}"

            if objects.get(name):
                objects[name][i] = o_id
            else:
                objects[name] = {i:o_id}
                if i == 0:
                    objects[name][1] = None
                else:
                    objects[name][0] = None
        
    return objects

def diff(f, t):
    '''
    Prints the changes when going from commit f to commit t.
    '''
    f = base.get_commit(f)
    t = base.get_commit(t)
    files = compare_snaps(f.tree, t.tree)

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
    
    # just in case
    return files


def merge(f_o_id, t_o_id):
    '''
    Merge commit f_o_id to commit t_o_id.\n
    It will update the current snapshot to merged snapshot.
    '''
    f = base.get_commit(f_o_id)     # head file
    t = base.get_commit(t_o_id)     # branch file which is to be merged into head
    merged_snap = {}
    files = compare_snaps(f.tree, t.tree)
    
    # writing the merged to current snapshot and creating a new one and committing it.
    for filename, o_ids in files.items():
        print(filename)
        if o_ids[0] and o_ids[1]:
            merged = merge_blobs(o_ids[0], o_ids[1])
            print(merged)
        elif o_ids[0]:
            print("created")
            with open(filename, 'w') as f:
                f.write(data.get_object(o_ids[0], expected='blob').decode().split("\r"))

        elif o_ids[1]:
            print("deleted")
            os.remove(filename)
        print()

    base.snapshot()
    base.commit("Merge commit")


def merge_blobs(branch, head):
    '''
    Merges two files. If conflicts arises, then will be indicated.\n
    Returns the merged file.
    '''
    branch = data.get_object(branch, expected='blob').decode().split("\r")
    head = data.get_object(head, expected='blob').decode().split("\r")

    diff = difflib.ndiff(head, branch)
    # print('branch:', branch, '\nhead:', head)
    # print('diff: ',list(diff))
    # print('\n')
    
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
    
    # print("\n".join(output))
    if conflict_occur: print("Conflict Occured!")
    return output
