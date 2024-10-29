# this will be used for high level implementation using base

from . import data
import os, shutil
import zlib
import datetime


def tag(tag_name, o_id):
    data.set_ref(f'refs\\tags\{tag_name}', o_id)

def checkout(tag_name = None, o_id = None):
    if tag_name:
        o_id = data.get_ref(f'refs\\tags\\{tag_name}')
        if not o_id:
            print("This tag doesn't point to any commit!")
            return
    
    c = get_commit(o_id)
    read_tree(c.tree)
    data.set_ref('HEAD', o_id)

def log_(o_id = None):
    # if not o_id:
    if o_id is None:
        o_id = data.get_ref('HEAD')
    commit = data.get_object(o_id, expected='commit').decode().split("\n")
    entries = []

    while len(commit) > 4:
        parent_o_id = commit[1]
        print("\n".join(commit), "\n")
        commit = data.get_object(parent_o_id.split(" ")[1], 'commit').decode().split("\n")
    print("\n".join(commit), "\n")

class Commit:
    def __init__(self, tree, author, time, msg, parent = None, tag = None):
        self.tree = tree
        self.parent = parent
        self.author = author
        self.time = time
        self.msg = msg

def commit(msg = "No message left"):
    commit = f"tree {write_tree()}\n"

    head = data.get_ref('HEAD')                                  # retrieve the parent commit of this
    if head:
        print(head)
        commit += f"parent {head}\n"                        # attach the parent head to the commit

    commit += f"author x\ntime {datetime.datetime.now()}\nmessage {msg}"

    o_id = data.hash_object(commit.encode(), 'commit')      # generate the o_id for this commit
    data.set_ref('HEAD', o_id)                                     # set the current commit as the head, as this is the latest commit

    # now this has become like a linked list, with links as parent_o_id
    return o_id

def get_commit(o_id):
    commit = data.get_object(o_id, 'commit').decode().splitlines()
    entries = []
    if len(commit) > 4:
        return Commit(
            commit[0].split(" ", 1)[1],
            commit[2].split(" ", 1)[1],
            commit[3].split(" ", 1)[1],
            commit[4].split(" ", 1)[1],
            commit[1].split(" ", 1)[1]
        )
    
    return Commit(
        commit[0].split(" ", 1)[1],
        commit[1].split(" ", 1)[1],
        commit[2].split(" ", 1)[1],
        commit[3].split(" ", 1)[1]
    )



def write_tree(directory = "."):
    # at the end you simply want to get the object id of this directory
    entries = []
    ignore = set()
    if os.path.exists(".trackitignore"):
        with open(".trackitignore", 'r') as f:
            ignore = set(f.read().split("\n"))

    with os.scandir(directory) as itr:
        for i in itr:
            curr = os.path.join(directory, i.name)
            
            if i.name == '.trackit' or i.name in ignore: continue

            if i.is_dir(follow_symlinks=False):
                object_type = 'tree'
                o_id = write_tree(curr)                     # this is a recursive algo for getting the o_id of the this dir
            else:
                object_type = 'blob'
                with open(curr, 'rb') as f:
                    o_id = data.hash_object(f.read())

            entries.append((object_type, o_id, i.name))

    tree = "".join(f"{object_type} {oid} {name}\n" for object_type, oid, name in entries)
    
    return data.hash_object(tree.encode(), 'tree')
    

def read_tree(o_id, base_path = '.'):
    obj_path = os.path.join(data.GIT_DIR, 'objects', o_id[:2], o_id[2:])

    with open(obj_path, 'rb') as f:
        r = f.read()

    content = zlib.decompress(r).split(b'\0', 1)[1]
    content = content.decode()

    del_list = {i:1 for i in os.listdir(base_path) if i != '.trackit'}

    # if os.path.exists(".trackitignore"):
    try:
        with open(".trackitignore", 'r') as f:
            ignore = f.readlines()
        for i in ignore:
            del_list.pop(i, None)
    except FileNotFoundError: pass
    
    for item in content.split("\n"):
        if not item: continue
        item_type, o_id, name = item.split(" ", 2)
        curr_path = os.path.join(base_path, name)

        try:
            del_list.pop(name)
        except KeyError:
            pass


        if item_type == 'tree':
            print(curr_path)
            try:
                os.mkdir(curr_path)
            except: pass
            read_tree(o_id, base_path = curr_path)
        else:
            with open(curr_path, 'w') as f:
                f.write(data.get_object(o_id).decode())

    for i in del_list:
        p = os.path.join(base_path, i)
        if os.path.isfile(p):
            os.remove(p)
        else:
            shutil.rmtree(p)