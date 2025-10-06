"""
This module provides various functions and classes to manage a version control system similar to Git.
It includes functionalities for creating commits, branches, tags, merging branches, and more.
Functions:
    get_merge_base(o1, o2):
        Returns the commit id of the common ancestor of two commits.
    delete_ref(name):
        Deletes the reference by its name.
    get_ref_path(ref):
        Returns the path of the reference using its name.
    merge(other, head):
        Merges the specified branch into the head branch.
    status():
        Prints the current branch we are on.
    reset(o_id):
        Resets the head and branch to a particular commit.
    show(o_id):
    get_all_branches():
        Prints the names of all branches, along with the current branch.
    tag(tag_name, o_id):
        Tags a commit with a specified name.
    checkout(ref_name=None, o_id=None):
        Checks out to a commit or reference.
    branch(name, o_id):
        Creates a branch with the specified name and commit id.
    log_(o_id=None, ref_name=None):
        Prints the chain of commits with respect to the current commit.
    commit(msg="No message left"):
        Creates a commit with the specified message and returns the commit id.
    get_commit(o_id):
        Returns the commit object for a particular commit id.
    iter_commits_and_parents(oid):
        Yields the commit id of the commit and all its parent commits.
    snapshot(directory="."):
        Creates a snapshot for the current directory structure and returns the object id of this directory.
    read_snapshot(o_id, base_path='.'):
        Writes the current file structure as per the snapshot.
Classes:
    Commit:
        Represents a commit object with attributes like snapshot, author, time, message, and parents.
"""


from . import data
from . import diffs
import os, shutil
import zlib
import datetime
import collections


def get_merge_base(o1, o2):
    '''
    Returns the commit id of the common ancestor.
    '''
    parents1 = set(iter_commits_and_parents(o1))

    for o in iter_commits_and_parents(o2):
        if o in parents1:
            return o

def delete_ref(name):
    '''
    Deletes the reference.
    '''
    path = get_ref_path(name)
    os.remove(path)

def get_ref_path(ref):
    '''
    Returns the path of the reference using it's name.
    '''
    potential_paths = [f"{ref}", f"refs\\heads\\{ref}", f"refs\\tags\\{ref}"]
    for path in potential_paths:
        if os.path.exists(f"{data.GIT_DIR}\\{path}"):
            return f"{data.GIT_DIR}\\{path}"
    return None

def merge(other, head):
    '''
    Merges the branch into head.
    '''
    other = data.get_ref(f'refs\\heads\\{other}')
    head = data.get_ref(f'refs\\heads\\{head}')
    
    other_commit = get_commit(other).snap
    head_commit = get_commit(head).snap

    diffs.merge_snaps(other_commit, head_commit)

    data.set_ref('MERGE_HEAD', other)
    print("Merged! Please make a commit to record the changes!")


def status():
    '''
    Prints the current branch we are on (latter on we will update it to even display the unstaged files).
    '''
    if data.check_symbolic():
        print(f"On branch {os.path.split(data.get_head_branch())[1]}")
    else:
        print(f"HEAD detached at {data.get_ref('HEAD')}")


def reset(o_id):
    '''
    This is different than checkout as in this case, the head as well as the branch would be set to a particular commit.
    This is not the case with checkout as checkout will just point the head to a commit.
    '''
    if data.check_symbolic():
        data.set_ref(data.get_head_branch(), o_id)
    else:
        data.set_head(o_id=o_id)
    c = get_commit(o_id=o_id)
    read_snapshot(c.snap)


def show(o_id):
    '''
    Prints the current commit details and diffs between the commit and its parent commit.
    '''
    cmt = get_commit(o_id)
    print(f"commit {o_id}\nauthor: {cmt.author}\ndate: {cmt.time}\nmessage: {cmt.msg}\n")
    p = cmt.parents
    # diffs.diff(cmt.parents[0], o_id)  # from, to
    
    if p:
        diffs.diff(p[0], o_id)
    else:
        print("This is the initial commit - no parent to compare with.")


def get_all_branches():
    '''
    Prints the names of all branches, along with with what branch we are pointing to right now
    '''
    head = None
    if data.check_symbolic():
        head = os.path.split(data.get_head_branch())[-1]

    for branch in os.listdir(os.path.join(data.GIT_DIR, 'refs', 'heads')):
        if head and branch == head:
            print("* " + branch)
        else:
            print("  " + branch)


def tag(tag_name, o_id):
    '''
    This is used to tag a commit
    '''
    data.set_ref(os.path.join('refs', 'tags', tag_name), o_id)


def checkout(ref_name = None, o_id = None):
    '''
    To checkout to a commit. Again this only changes the head position, branch will be unaffected.
    '''
    if ref_name:
        for ref, id in data.iter_refs():
            if not id: continue
            if os.path.split(ref)[-1] == ref_name:
                o_id = id
                if ref.split("\\")[1] == 'heads':
                    data.set_head(ref = ref)
                else:
                    data.set_head(o_id = o_id)
                try:
                    c = get_commit(o_id)
                    print(o_id)
                    read_snapshot(c.snap)
                except: print("Invalid reference")
                return

        if not o_id:
            print("This tag doesn't point to any commit!")
            return

    c = get_commit(o_id)
    read_snapshot(c.snap)
    data.set_head(o_id = o_id)

def branch(name, o_id):
    '''
    Creates a branch.
    '''
    data.set_ref(os.path.join('refs', 'heads', name), o_id)


def log_(o_id = None, ref_name = None):
    '''
    Prints the chain of commits wrt current commit (it and all its parent commits).
    '''
    if not o_id:
        if ref_name:
            o_id = data.get_ref(f'refs\\tags\\{ref_name}')
            if o_id is None:
                o_id = data.get_ref(f'refs\\heads\\{ref_name}')
            
            if o_id is None:
                print("This reference doesn't exist!")
                return
        else:
            o_id = data.get_ref('HEAD')
    commit = data.get_object(o_id, expected='commit').decode().split("\n")
    
    refs = {}
    for refname, refv in data.iter_refs():
        if not refv: continue
        refs.setdefault(refv, []).append(os.path.split(refname)[-1])
    while len(commit) > 4:
        parent_o_id = commit[1].split(' ')[1]
        if refs.get(o_id):
            print(", ".join(refs[o_id]))
        print(f"commit {o_id}\n" + "\n".join(commit), "\n")

        commit = data.get_object(parent_o_id, 'commit').decode().split("\n")
        o_id = parent_o_id
    print(f"commit {o_id}\n" + "\n".join(commit), "\n")


class Commit:
    def __init__(self, snap, author, time, msg, parents = None):
        self.snap = snap
        self.parents = parents
        self.author = author
        self.time = time
        self.msg = msg


def commit(msg = "No message left"):
    '''
    Creates a commit.
    Returns the object id of commit.
    '''

    commit = f"snap {snapshot()}\n"

    head = data.get_ref('HEAD')                                 # retrieve the parent commit of this
    if head:
        commit += f"parent {head}\n"                            # attach the parent head to the commit
    
    merged_head = data.get_ref('MERGE_HEAD')
    if merged_head:
            commit += f"parent {merged_head}\n"
            delete_ref('MERGE_HEAD')

    commit += f"author x\ntime {datetime.datetime.now()}\nmessage {msg}"

    o_id = data.hash_object(commit.encode(), 'commit')          # generate the o_id for this commit
    
    branch = data.get_head_branch()

    print(f"[{os.path.split(branch)[-1]}] {msg}")
    data.set_ref(branch, o_id)                                  # set the current commit as the head, as this is the latest commit

    # now this has become like a linked list, with links as parent_o_id
    return o_id

def get_commit(o_id):
    '''
    Returns the commit wrt to a particular commit id.
    '''
    commit = iter(data.get_object(o_id, 'commit').decode().splitlines())
    attr = {'parents':[]}
    for c in commit:
        x = c.split(" ", 1)
        if x[0] == 'parent':
            attr['parents'].append(x[1])
        else:
            attr[x[0]] = x[1]

    return Commit(
        snap = attr['snap'],
        author = attr['author'],
        time = attr['time'],
        msg = attr['message'],
        parents = attr['parents'],
    )

def iter_commits_and_parents(oid):
    '''
    Gets the commit as well as all of its parental commits. Yeilds commit ID.
    '''

    oids = collections.deque({oid})
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid

        commit = get_commit(oid)
        oids.extendleft(commit.parents[:1])
        oids.extend(commit.parents[1:])


def snapshot(directory = "."):
    '''
    Creates a snapshot for the current directory structure and get the object id of this directory.
    '''
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
                object_type = 'snap'
                o_id = snapshot(curr)                     # this is a recursive algo for getting the o_id of the this dir
            else:
                object_type = 'blob'
                with open(curr, 'rb') as f:
                    o_id = data.hash_object(f.read())

            entries.append((object_type, o_id, i.name))

    snap = "".join(f"{object_type} {oid} {name}\n" for object_type, oid, name in entries)
    
    return data.hash_object(snap.encode(), 'snap')

def read_snapshot(o_id, base_path = '.'):
    '''
    Writes the current file structure as per the snapshot.
    '''
    obj_path = os.path.join(data.GIT_DIR, 'objects', o_id[:2], o_id[2:])

    with open(obj_path, 'rb') as f:
        r = f.read()

    content = zlib.decompress(r).split(b'\0', 1)[1].decode()

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


        if item_type == 'snap':
            try:
                os.mkdir(curr_path)
            except: pass
            read_snapshot(o_id, base_path = curr_path)
        else:
            with open(curr_path, 'w') as f:
                f.write(data.get_object(o_id).decode())
    
    for i in del_list:
        p = os.path.join(base_path, i)
        if os.path.isfile(p):
            os.remove(p)
        else:
            shutil.rmtree(p)