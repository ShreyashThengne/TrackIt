# this will be used for high level implementation using base

from . import data
import os
import zlib

def write_tree(directory = "."):
    # at the end you simply want to get the object id of this directory
    entries = []
    with open(".trackitignore", 'r') as f:
        ignore = f.read().split("\n")

    with os.scandir(directory) as itr:
        for i in itr:
            curr = os.path.join(directory, i.name)
            
            if i.name == '.trackit' or i.name in ignore: continue

            if i.is_dir(follow_symlinks=False):
                object_type = 'tree'
                o_id = write_tree(curr)   #this is a recursive algo for getting the o_id of the this dir
            else:
                object_type = 'blob'
                with open(curr, 'rb') as f:
                    o_id = data.hash_object(f.read())

            entries.append((object_type, o_id, i.name))
    entries.sort()
    tree = "".join(f"{object_type} {oid} {name}\n" for object_type, oid, name in entries)
    
    return data.hash_object(tree.encode(), 'tree')
    

def read_tree(o_id, base_path = ''):

    obj_path = os.path.join(data.GIT_DIR, 'objects', o_id[:2], o_id[2:])

    with open(obj_path, 'rb') as f:
        r = f.read()
        
    header, content = zlib.decompress(r).split(b'\0', 1)
    header = header.decode()
    content = content.decode()
    
    for item in content.split("\n"):
        if not item: continue
        # print("H", item, item.split(" ", 3))
        item_type, o_id, name = item.split(" ", 2)
        if item_type == 'tree':
            read_tree(o_id, base_path = os.path.join(base_path, name))
        else:
            try:
                with open(os.path.join(base_path, name), 'w') as f:
                    f.write(data.get_object(o_id).decode())
            except FileNotFoundError:
                print("File not found!")