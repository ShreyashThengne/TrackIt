import argparse
from . import data
from . import base
import os, sys


def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='cmd')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func = init)

    hash_file_parser = commands.add_parser('hash_file')
    hash_file_parser.set_defaults(func = hash_object)
    hash_file_parser.add_argument('obj')

    cat_file_parser = commands.add_parser('cat_file')
    cat_file_parser.set_defaults(func = cat_object)
    cat_file_parser.add_argument('obj')

    write_tree_parser = commands.add_parser('write_tree')
    write_tree_parser.set_defaults(func = write_tree)

    read_tree_parser = commands.add_parser('read_tree')
    read_tree_parser.set_defaults(func = read_tree)
    read_tree_parser.add_argument('tree')

    return parser.parse_args()

def write_tree(arg):
    print(base.write_tree())

def read_tree(arg):
    print(base.read_tree(arg.tree))

def hash_object(arg):
    with open(arg.obj, 'rb') as f:
        content = f.read()
    o_id = data.hash_object(content)  # content is in binary form
    print(o_id)

def cat_object(arg):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(arg.obj, expected = None))



# ***************************

def init(args):
    data.init()
    print(f"Initialised trackit repository at {os.getcwd()}\{data.GIT_DIR}. As of now its not tracking anything.")

def main():
    args = parse_args()
    args.func(args)