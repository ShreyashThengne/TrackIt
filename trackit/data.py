import os
import hashlib
import zlib

GIT_DIR = ".trackit"

def init():
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f"{GIT_DIR}\objects", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs\heads", exist_ok=True)
    os.makedirs(f"{GIT_DIR}\\refs\\tags", exist_ok=True)
    set_head(ref = 'refs\heads\main')
    
def hash_object(content, obj_type="blob"):
    '''
    hash the object content and store it in the .trackit/objects
    output: o_id
    '''

    # '\0' is used to divide the header with content. Again we then encode the header to binary
    header = f"{obj_type} {len(content)}\0".encode()

    # content is already in binary format
    headed_content = header + content
    o_id = hashlib.sha1(headed_content).hexdigest()     #hashes using sha1 to get the object id

    # we divide the files with respect to their oid with first 2 characters as directory and the rest as file name
    obj_dir_path = os.path.join(GIT_DIR, 'objects', o_id[:2])
    os.makedirs(obj_dir_path, exist_ok = True)

    # compress the file to save storage
    with open(os.path.join(obj_dir_path, o_id[2:]), 'wb') as f:
        f.write(zlib.compress(headed_content))
    
    return o_id

def get_object(o_id, expected = 'blob'):
    '''
    retrieves the object content withe reference to the object id
    output: binary codec
    '''
    try:
        # we first get the file, then we decompress it and then get the header and content using '\0' as reference.
        # now we decode the header to original format

        obj_path = os.path.join(GIT_DIR, 'objects', o_id[:2], o_id[2:])
        # print(obj_path)
        with open(obj_path, 'rb') as f:
            r = f.read()
        
        header, content = zlib.decompress(r).split(b'\0', 1)
        content_type = header.decode().split(" ")[0]
        content_size = header.decode().split(" ")[1]

        if expected:
            if expected != content_type: return f'Expected {expected}, got {content_type}'

        return content
    
    except FileNotFoundError:
        print(f"Object {o_id} not found.")
        return None
    
def set_head(ref = None, o_id = None):
    with open(os.path.join(GIT_DIR, 'HEAD'), 'w') as f:
        if ref:
            f.write(f"ref: {ref}")
        else:
            f.write(f"commit: {o_id}")

def set_ref(ref, o_id):
    with open(os.path.join(GIT_DIR, ref), 'w') as f:
        f.write(o_id)

def get_head_branch():
    with open(os.path.join(GIT_DIR, 'HEAD'), 'r') as f:
        return f.read().split(" ")[1]

def get_ref(ref):
    path = os.path.join(GIT_DIR, ref)

    if ref == 'HEAD':
        with open(path, 'r') as f:
            r = f.read().split(" ")
            if r[0] == 'commit:':
                return r[1]
            path = os.path.join(GIT_DIR, r[1])
    
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def iter_refs():
    refs = ['HEAD']
    # print('uhjwds',os.path.join(GIT_DIR, 'refs'))
    for root, dirs, files in os.walk(os.path.join(GIT_DIR, 'refs')):
        root = os.path.relpath(root, GIT_DIR)                   # this is done in order to remove GIT_DIR part from the path
        refs.extend([os.path.join(root, i) for i in files])
    
    for ref in refs:
        yield ref, get_ref(ref)

def check_symbolic():
    with open(os.path.join(GIT_DIR, 'HEAD'), 'r') as f:
        r = f.read()
        if r.split(" ")[0] == 'commit:':
            return False
        return True
