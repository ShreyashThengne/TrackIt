import argparse
from . import data
from . import base
from . import diffs
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

    cat_file_parser = commands.add_parser('read_file')
    cat_file_parser.set_defaults(func = read_object)
    cat_file_parser.add_argument('obj')     # extra arg to be stored in obj variable

    write_tree_parser = commands.add_parser('snapshot')
    write_tree_parser.set_defaults(func = snapshot)

    read_tree_parser = commands.add_parser('read-snapshot')
    read_tree_parser.set_defaults(func = read_snapshot)
    read_tree_parser.add_argument('tree')

    commit_parser = commands.add_parser('commit')
    commit_parser.set_defaults(func = commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser = commands.add_parser('log')
    log_parser.set_defaults(func = log_)
    log_parser.add_argument('o_id', nargs='?')
    log_parser.add_argument('-r', '--ref', required=False)

    checkout_parser = commands.add_parser('checkout')
    checkout_parser.set_defaults(func = checkout)
    checkout_parser.add_argument('o_id', nargs='?')
    checkout_parser.add_argument('-r', '--ref', required=False)

    tag_parser = commands.add_parser('tag')
    tag_parser.set_defaults(func = tag)
    tag_parser.add_argument('tag_name')
    tag_parser.add_argument('o_id', nargs='?')

    k_parser = commands.add_parser ('status')
    k_parser.set_defaults(func=status)

    branch_parser = commands.add_parser('branch')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('o_id', nargs='?')

    reset_parser = commands.add_parser("reset")
    reset_parser.set_defaults(func = reset)
    reset_parser.add_argument("o_id")

    show_parser = commands.add_parser("show")
    show_parser.set_defaults(func = show)
    show_parser.add_argument("o_id", default=data.get_ref('HEAD'), nargs='?')

    diff_parser = commands.add_parser("diff")
    diff_parser.set_defaults(func = diff)
    diff_parser.add_argument("f_o_id", nargs='?')
    diff_parser.add_argument("t_o_id", default=data.get_ref('HEAD'), nargs='?')

    return parser.parse_args()

def snapshot(arg):
    print(base.snapshot())    # this will print o_id of the tree

def read_snapshot(arg):
    base.read-snapshot(arg.tree)    # this will restore the repo to a previously stored instance/tree using the given o_id

def commit(arg):
    print(base.commit(arg.message))

def log_(args):
    base.log_(args.o_id, args.ref)      # this ref can be either head or tag

def checkout(args):
    if args.o_id is None:
        if args.ref:
            base.checkout(ref_name = args.ref)
            return
        else:
            args.o_id = data.get_ref('HEAD')
    base.checkout(o_id = args.o_id)

def tag(args):
    base.tag(args.tag_name, args.o_id)

def status(args):
    base.status(args.o_id)

def branch(args):
    if not args.name and not args.o_id:
        base.get_all_branches()
        return
    
    if not args.o_id:
        args.o_id = data.get_ref('HEAD')

    base.branch(args.name, args.o_id)

def reset(args):
    base.reset(args.o_id)

def show(args):
    base.show(args.o_id)

def diff(args):
    if not args.f_o_id:
        c = base.get_commit(args.t_o_id)
        if not c.parent:
            print("This commit does not have any parent!")
            return
        args.f_o_id = c.parent
    diffs.diff(args.f_o_id, args.t_o_id)

def hash_object(arg):   # this is used to store the object and reference it with an o_id
    with open(arg.obj, 'rb') as f:
        content = f.read()
    o_id = data.hash_object(content)  # content is in binary form
    print(o_id)

def read_object(arg):    # this is used to retrieve the object content usign o_id
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(arg.obj, expected = None))



# ***************************

def init(args):
    data.init()
    print(f"Initialised an empty trackit repository at {os.getcwd()}\{data.GIT_DIR}.")

def main():
    args = parse_args()
    args.func(args)