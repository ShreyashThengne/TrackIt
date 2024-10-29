import argparse
from . import data
from . import base
import os, sys


def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='cmd')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func = init)   # when 'init' is parsed, init function will be triggered

    hash_file_parser = commands.add_parser('hash_file')
    hash_file_parser.set_defaults(func = hash_object)
    hash_file_parser.add_argument('obj')

    cat_file_parser = commands.add_parser('cat_file')
    cat_file_parser.set_defaults(func = cat_object)
    cat_file_parser.add_argument('obj')     # extra arg to be stored in obj variable

    write_tree_parser = commands.add_parser('write_tree')
    write_tree_parser.set_defaults(func = write_tree)

    read_tree_parser = commands.add_parser('read_tree')
    read_tree_parser.set_defaults(func = read_tree)
    read_tree_parser.add_argument('tree')

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func = commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func = log_)
    log_parser.add_argument('o_id', nargs='?')

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func = checkout)
    checkout_parser.add_argument('o_id', nargs='?')
    checkout_parser.add_argument('-t', '--tag', required=False)

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func = tag)
    tag_parser.add_argument('tag_name')
    tag_parser.add_argument('o_id', nargs='?')

    return parser.parse_args()

def write_tree(arg):
    print(base.write_tree())    # this will print o_id of the tree

def read_tree(arg):
    base.read_tree(arg.tree)    # this will restore the repo to a previously stored instance/tree using the given o_id

def commit(arg):
    print(base.commit(arg.message))

def log_(args):
    base.log_(args.o_id)

def checkout(args):
    if args.o_id is None:
        if args.tag:
            base.checkout(tag_name = args.tag)
            return
        else:
            args.o_id = data.get_head()
    base.checkout(o_id = args.o_id)

def tag(args):
    base.tag(args.tag_name, args.o_id)

def hash_object(arg):   # this is used to store the object and reference it with an o_id
    with open(arg.obj, 'rb') as f:
        content = f.read()
    o_id = data.hash_object(content)  # content is in binary form
    print(o_id)

def cat_object(arg):    # this is used to retrieve the object content usign o_id
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(arg.obj, expected = None))



# ***************************

def init(args):
    data.init()
    print(f"Initialised an empty trackit repository at {os.getcwd()}\{data.GIT_DIR}.")

def main():
    args = parse_args()
    args.func(args)