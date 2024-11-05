[33mcommit 10e1d1307f6d6e44ae4ccf60596e9b53658ce989[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmaster[m[33m)[m
Author: Shreyash Thengne <shreyashthengne@gmail.com>
Date:   Tue Nov 5 21:21:05 2024 +0530

    just testing

[1mdiff --git a/trackit/__pycache__/base.cpython-311.pyc b/trackit/__pycache__/base.cpython-311.pyc[m
[1mindex a7c7b9b..2c12c35 100644[m
Binary files a/trackit/__pycache__/base.cpython-311.pyc and b/trackit/__pycache__/base.cpython-311.pyc differ
[1mdiff --git a/trackit/__pycache__/cli.cpython-311.pyc b/trackit/__pycache__/cli.cpython-311.pyc[m
[1mindex e73d279..d0fa41e 100644[m
Binary files a/trackit/__pycache__/cli.cpython-311.pyc and b/trackit/__pycache__/cli.cpython-311.pyc differ
[1mdiff --git a/trackit/__pycache__/data.cpython-311.pyc b/trackit/__pycache__/data.cpython-311.pyc[m
[1mindex 971635b..062ed70 100644[m
Binary files a/trackit/__pycache__/data.cpython-311.pyc and b/trackit/__pycache__/data.cpython-311.pyc differ
[1mdiff --git a/trackit/__pycache__/diffs.cpython-311.pyc b/trackit/__pycache__/diffs.cpython-311.pyc[m
[1mnew file mode 100644[m
[1mindex 0000000..e06a086[m
Binary files /dev/null and b/trackit/__pycache__/diffs.cpython-311.pyc differ
[1mdiff --git a/trackit/base.py b/trackit/base.py[m
[1mindex 2387c25..bc8ee7a 100644[m
[1m--- a/trackit/base.py[m
[1m+++ b/trackit/base.py[m
[36m@@ -32,6 +32,12 @@[m [mdef reset(o_id):[m
     else:[m
         data.set_head(o_id=o_id)[m
 [m
[32m+[m[32mdef show(o_id):[m
[32m+[m[32m    cmt = get_commit(o_id).msg[m
[32m+[m[32m    print(cmt)[m
[32m+[m
[32m+[m
[32m+[m
 def get_all_branches():[m
     head = None[m
     if data.check_symbolic():[m
[1mdiff --git a/trackit/cli.py b/trackit/cli.py[m
[1mindex 37866bf..a24b514 100644[m
[1m--- a/trackit/cli.py[m
[1m+++ b/trackit/cli.py[m
[36m@@ -1,6 +1,7 @@[m
 import argparse[m
 from . import data[m
 from . import base[m
[32m+[m[32mfrom . import diffs[m
 import os, sys[m
 [m
 [m
[36m@@ -61,7 +62,12 @@[m [mdef parse_args():[m
 [m
     show_parser = commands.add_parser("show")[m
     show_parser.set_defaults(func = show)[m
[31m-    # reset_parser.add_argument("o_id")[m
[32m+[m[32m    show_parser.add_argument("o_id", default=data.get_ref('HEAD'), nargs='?')[m
[32m+[m
[32m+[m[32m    diff_parser = commands.add_parser("diff")[m
[32m+[m[32m    diff_parser.set_defaults(func = diff)[m
[32m+[m[32m    diff_parser.add_argument("f_o_id", nargs='?')[m
[32m+[m[32m    diff_parser.add_argument("t_o_id", default=data.get_ref('HEAD'), nargs='?')[m
 [m
     return parser.parse_args()[m
 [m
[36m@@ -90,7 +96,7 @@[m [mdef tag(args):[m
     base.tag(args.tag_name, args.o_id)[m
 [m
 def status(args):[m
[31m-    base.status()[m
[32m+[m[32m    base.status(args.o_id)[m
 [m
 def branch(args):[m
     if not args.name and not args.o_id:[m
[36m@@ -106,7 +112,14 @@[m [mdef reset(args):[m
     base.reset(args.o_id)[m
 [m
 def show(args):[m
[31m-    base.show()[m
[32m+[m[32m    base.show(args.o_id)[m
[32m+[m
[32m+[m[32mdef diff(args):[m
[32m+[m[32m    if not args.f_o_id:[m
[32m+[m[32m        c = base.get_commit(args.t_o_id)[m
[32m+[m[32m        args.f_o_id = c.parent[m
[32m+[m[32m        # print(args.t_o_id)[m
[32m+[m[32m    print(diffs.diff(args.f_o_id, args.t_o_id))[m
 [m
 def hash_object(arg):   # this is used to store the object and reference it with an o_id[m
     with open(arg.obj, 'rb') as f:[m
[1mdiff --git a/trackit/diffs.py b/trackit/diffs.py[m
[1mnew file mode 100644[m
[1mindex 0000000..ce3547c[m
[1m--- /dev/null[m
[1m+++ b/trackit/diffs.py[m
[36m@@ -0,0 +1,65 @@[m
[32m+[m[32mfrom . import base[m
[32m+[m[32mfrom . import data[m
[32m+[m[32mimport difflib[m
[32m+[m
[32m+[m[32mdef compare_snaps(s1, s2, path = "."):[m
[32m+[m[32m    objects = {}[m
[32m+[m[32m    for i, s in enumerate([s1, s2]):[m
[32m+[m[32m        snap = data.get_object(s, expected='tree').decode().split("\n")[m
[32m+[m[32m        for obj in snap[:-1]:[m
[32m+[m[32m            o = obj.split(" ", 2)[m
[32m+[m[32m            type = o[0][m
[32m+[m
[32m+[m[32m            o_id = o[1][m
[32m+[m[32m            if type == 'tree':[m
[32m+[m[32m                sub_path = f"{path}\{o[2]}"[m
[32m+[m[32m                sub_objects = compare_snaps(o_id, o_id, sub_path)[m
[32m+[m
[32m+[m[32m                for sub_name, sub_obj in sub_objects.items():[m
[32m+[m[32m                    if objects.get(sub_name):[m
[32m+[m[32m                        objects[sub_name][i] = sub_obj[i][m
[32m+[m[32m                    else:[m
[32m+[m[32m                        objects[sub_name] = sub_obj[m
[32m+[m[32m                        if i == 0:[m
[32m+[m[32m                            objects[sub_name][1] = None[m
[32m+[m[32m                        else:[m
[32m+[m[32m                            objects[sub_name][0] = None[m
[32m+[m[32m                continue[m
[32m+[m[41m                [m
[32m+[m
[32m+[m[32m            name = f"{path}\{o[2]}"[m
[32m+[m
[32m+[m[32m            if objects.get(name):[m
[32m+[m[32m                objects[name][i] = o_id[m
[32m+[m[32m            else:[m
[32m+[m[32m                objects[name] = {i:o_id}[m
[32m+[m[32m                if i == 0:[m
[32m+[m[32m                    objects[name][1] = None[m
[32m+[m[32m                else:[m
[32m+[m[32m                    objects[name][0] = None[m
[32m+[m[41m        [m
[32m+[m[32m    return objects[m
[32m+[m
[32m+[m[32mdef diff(t, f):[m
[32m+[m[32m    f = base.get_commit(f)[m
[32m+[m[32m    t = base.get_commit(t)[m
[32m+[m[32m    files = compare_snaps(f.tree, t.tree)[m
[32m+[m[32m    print(files)[m
[32m+[m
[32m+[m[32m    # for filename, o_ids in files.items():[m
[32m+[m[32m    #     # print(filename, o_ids)[m
[32m+[m[41m        [m
[32m+[m[32m    #     if o_ids[0] == o_ids[1]: continue[m
[32m+[m[32m    #     elif o_ids[0] and not o_ids[1]:[m
[32m+[m[32m    #         print(f"{filename} was deleted!")[m
[32m+[m[32m    #     elif not o_ids[0] and o_ids[1]:[m
[32m+[m[32m    #         print(f"{filename} was added!")[m
[32m+[m[32m    #     else:[m
[32m+[m[32m    #         # this means the file was modified[m
[32m+[m[32m    #         file1 = base.read_snapshot(o_ids[0])[m
[32m+[m[32m    #         file2 = base.read_snapshot(o_ids[1])[m
[32m+[m[32m    #         print(filename)[m
[32m+[m[32m    #         d = difflib.unified_diff(file1, file2)[m
[32m+[m[32m    #         for line in d:[m
[32m+[m[32m    #             print(line)[m
[32m+[m[41m    [m
\ No newline at end of file[m
