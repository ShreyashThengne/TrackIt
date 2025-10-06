# TrackIt

TrackIt is a basic version control system inspired by Git. It provides functionalities for creating commits, branches, tags, merging branches, and more.

I have published this package on PyPIP. Here's the link: https://pypi.org/project/trackit-vcs/

## Installation

Using PIP:
```sh
pip install trackit-vcs
```

or 

Clone it at a desired directory. Open a terminal in that directory.\
To install this package, run:

```sh
pip install .
```

## Usage
TrackIt provides a command-line interface (CLI) for interacting with the version control system. Below are some of the commands you can use:

Initialize a Repository\
To initialize a new TrackIt repository, run:
```sh
trackit init
```

Create a Snapshot\
To create a snapshot of the current state of the repository, run:
```sh
trackit snapshot
```

Read a Snapshot
To restore the repository to a previously stored snapshot, run:
```sh
trackit read-snapshot <snapshot_id>
```

Commit Changes\
To commit changes to the repository with a message, run:
```sh
trackit commit -m "Your commit message"
```

View Commit Log\
To display the commit log, run:
```sh
trackit log
```
Checkout a Commit or Reference\
To checkout a specific commit, run:
```sh
trackit checkout <commit_id_or_ref>
```
or reference(tag or branch), run:
```sh
trackit checkout -r <ref>
```
Create a Branch
To create a new branch, run:
```sh
trackit branch <branch_name>
```

Tag a Commit\
To tag a specific commit with a name, run:
```sh
trackit tag <tag_name> <commit_id>
```

Show Commit Details\
To show the content of a specific commit, run:
```sh
trackit show <commit_id>
```

Display Differences Between Commits\
To display the differences between two commits, run:
```sh
trackit diff <from_commit_id> <to_commit_id>
```

Merge Branches\
To merge two branches, run:
```sh
trackit merge <other_branch> <head_branch>
```

Find Common Ancestor of Two Commits\
To find the common ancestor of two commits, run:
```sh
trackit merge-base <commit_id1> <commit_id2>
```

Status\
View the status, run:
```sh
trackit status
```

Reset\
To reset the repository to a specific commit, run:
```sh
trackit reset <commit_id>
```

Find Common Ancestor of Two Commits
To find the common ancestor of two commits, run:
```sh
trackit merge-base <commit_id1> <commit_id2>
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgements
This project is inspired by Git and aims to provide similar functionalities for version control.
