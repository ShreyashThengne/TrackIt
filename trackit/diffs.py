from . import base
from . import data
import difflib

def compare_snaps(s1, s2, path = "."):
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
    f = base.get_commit(f)
    t = base.get_commit(t)
    files = compare_snaps(f.tree, t.tree)

    for filename, o_ids in files.items():
        
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
            print(file1, file2)
            d = difflib.unified_diff(file1, file2, lineterm='')
        
            for line in d:
                print(line)
        print()
    
    return files

def merge(f_o_id, t_o_id):
    f = base.get_commit(f_o_id)     # head file
    t = base.get_commit(t_o_id)     # branch file which is to be merged into head
    merged_snap = {}
    files = compare_snaps(f.tree, t.tree)

    for filename, o_ids in files:
        pass

def merge_blobs(f, t):
    f = data.get_object(f, expected='blob').decode().split("\r")
    t = data.get_object(t, expected='blob').decode().split("\r")
    
    d = difflib.unified_diff(f, t, lineterm='')[2:]
    i = 0
    while i < len(d):
        if d[i].startswith('-'):
            print("<<<<<<< HEAD")
            while d[i].startswith('-'):
                print(d[i][1:])
                i += 1
            while i < len(d) and d[i].startswith('+'):
                print(d[i][1:])
                i += 1
            print(">>>>>>branch")
        else:
            print(d[i][1:])


        # if f[i] != t[j]: # \n{t[j]}\n>>>>>>branch
        #     res += f[i]
        #     i += 1
        #     j += 1