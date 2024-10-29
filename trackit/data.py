import os
import hashlib
import zlib

GIT_DIR = ".trackit"

def init():
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f"{GIT_DIR}\objects", exist_ok=True)

def hash_object(content, obj_type="blob"):
    header = f"{obj_type} {len(content)}\0".encode()

    # content is already in binary format
    headed_content = header + content
    o_id = hashlib.sha1(headed_content).hexdigest()  #object id

    obj_dir_path = os.path.join(GIT_DIR, 'objects', o_id[:2])
    os.makedirs(obj_dir_path, exist_ok = True)

    with open(os.path.join(obj_dir_path, o_id[2:]), 'wb') as f:
        f.write(zlib.compress(headed_content))
    
    return o_id

def get_object(o_id, expected = 'blob'):
    try:
        obj_path = os.path.join(GIT_DIR, 'objects', o_id[:2], o_id[2:])
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