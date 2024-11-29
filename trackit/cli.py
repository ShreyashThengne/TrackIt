"""
This module provides a command-line interface (CLI) for the Trackit version control system. It uses the argparse library to parse command-line arguments and execute corresponding functions. The module supports various commands such as initializing a repository, committing changes, creating branches, tagging, and more.
Functions:
- init(args): Initializes a new Trackit repository.
- parse_args(): Parses command-line arguments and sets up subparsers for different commands.
- snapshot(arg): Creates a snapshot of the current state of the repository.
- read_snapshot(arg): Restores the repository to a previously stored snapshot.
- commit(arg): Commits changes to the repository with a message.
- log_(args): Displays the commit log.
- checkout(args): Checks out a specific commit or reference.
- tag(args): Tags a specific commit with a name.
- status(args): Displays the current status of the repository.
- branch(args): Manages branches in the repository.
- reset(args): Resets the repository to a specific commit.
- show(args): Shows the content of a specific commit.
- diff(args): Displays the differences between two commits.
- merge(args): Merges two branches.
- merge_base(args): Finds the common ancestor of two commits.
- hash_object(arg): Hashes a file and stores it as an object in the repository.
- read_object(arg): Retrieves the content of an object using its hash.
The main() function is the entry point of the CLI, which parses the arguments and calls the appropriate function based on the command provided.
"""

import argparse
from . import data
from . import base
from . import diffs
import os, sys


def init(args):
    data.init()
    print(f"Initialised an empty trackit repository at {os.getcwd()}\{data.GIT_DIR}.")

def parse_args():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='cmd')
    commands.required = True

    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func = init)   # when 'init' is parsed, init function will be triggered

    hash_file_parser = commands.add_parser('hash-file')
    hash_file_parser.set_defaults(func = hash_object)
    hash_file_parser.add_argument('obj')

    cat_file_parser = commands.add_parser('read-file')
    cat_file_parser.set_defaults(func = read_object)
    cat_file_parser.add_argument('obj')     # extra arg to be stored in obj variable

    write_tree_parser = commands.add_parser('snapshot')
    write_tree_parser.set_defaults(func = snapshot)

    read_tree_parser = commands.add_parser('read-snapshot')
    read_tree_parser.set_defaults(func = read_snapshot)
    read_tree_parser.add_argument('snap')

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

    status_parser = commands.add_parser ('status')
    status_parser.set_defaults(func=status)

    branch_parser = commands.add_parser('branch')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('o_id', nargs='?')

    reset_parser = commands.add_parser("reset")
    reset_parser.set_defaults(func = reset)
    reset_parser.add_argument("o_id")

    show_parser = commands.add_parser("show")
    show_parser.set_defaults(func = show)
    show_parser.add_argument("o_id", nargs='?')

    diff_parser = commands.add_parser("diff")
    diff_parser.set_defaults(func = diff)
    diff_parser.add_argument("f_o_id", nargs='?')
    diff_parser.add_argument("t_o_id", nargs='?')

    merge_parser = commands.add_parser("merge")
    merge_parser.set_defaults(func = merge)
    merge_parser.add_argument("other_branch")
    merge_parser.add_argument("head_branch", default='main', nargs='?')

    merge_base_parser = commands.add_parser ('merge-base')
    merge_base_parser.set_defaults (func=merge_base)
    merge_base_parser.add_argument('o1')
    merge_base_parser.add_argument('o2')

    return parser.parse_args()

def main():
    args = parse_args()
    args.func(args)


''' ************************************************************************* '''

def snapshot(arg):
    print(base.snapshot())    # this will print o_id of the snap

def read_snapshot(arg):
    base.read_snapshot(arg.snap)    # this will restore the repo to a previously stored instance/snap using the given o_id

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
    base.status()

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
    if not args.o_id: args.o_id = data.get_ref('HEAD')
    base.show(args.o_id)

def diff(args):
    if not args.f_o_id:
        c = base.get_commit(args.t_o_id)
        if not c.parent:
            print("This commit does not have any parent!")
            return
        args.f_o_id = c.parent
    diffs.diff(args.f_o_id, args.t_o_id)

def merge(args):
    base.merge(args.other_branch, args.head_branch)

def merge_base(args):
    print(base.get_merge_base(args.o1, args.o2))

def hash_object(arg):   # this is used to store the object and reference it with an o_id
    with open(arg.obj, 'rb') as f:
        content = f.read()
    o_id = data.hash_object(content)  # content is in binary form
    print(o_id)

def read_object(arg):    # this is used to retrieve the object content usign o_id
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(arg.obj, expected = None))