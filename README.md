# Steemvote

This is a program that votes for posts on Steem. It uses piston and thus requires Python 3.

The included script, `steemvoter`, works by monitoring all comments on Steem.
If a comment is eligible for voting, it is stored in a database. The eligible comments
are periodically pulled from the database and voted on after they are a pre-set age.

## Installation

```
$ sudo python3 setup.py install
```

The above command will install all required dependencies.
You can run steemvoter like so: `steemvoter -c path/to/config.json`.

## Configuration

A configuration file specifies the authors to vote on, the key to sign votes with, etc.
Your configuration file can be supplied with a command-line argument (`steemvoter -c path/to/config.json`).
If not supplied, steemvoter will look for the file `steemvote-config.json` in the current directory.

An example config file, `example-steemvote-config.json`, is supplied.

The following config values are required:

- `authors`: A list of authors, and optional values for each (see below).
- `voter_account_name`: The name of your account.
- `vote_key`: The private key used to sign votes with (This should be your "Posting" key).

### Authors

The `authors` list in your config file contains a list of objects.
Each object needs a `name` value, which is the name of the author.

Optional values for each author:

- `vote_replies`: Whether to vote on all replies the author makes, in addition to their regular posts (Default: `false`).
- `weight`: The weight to vote with. `100.0` represents an upvote, and `-100.0` represents a downvote (Default: `100.0`).

### Voting Rules

The following values are optional, and specify how to vote:

- `max_post_age`: The maximum age of a post (Default: `2 days`).
- `vote_delay`: The age a post must be before it is voted on (Default: `1 minute`).

These values can be specified as seconds or as human-readable strings (e.g. `"max_post_age": "2 days"`).

### Database

By default, the database of posts will be a folder called `database` in the current directory.
This behavior can be changed using the `database_path` config value.

### RPC

If no RPC options are specified, a public node will be used.

Available RPC options:

- `rpc_node`: The URL of the node to connect to.
- `rpc_user`: RPC username to use.
- `rpc_pass`: RPC password to use.

## Example Configurations

Upvote every post by [@klye](http://steemit.com/@klye), including his replies to other posts.
Wait until posts are 30 seconds old to upvote them.

```
{
    "authors": [
        {"name": "klye", "vote_replies": true}
    ],
    "vote_key": "5XX...",
    "voter_account_name": "myname",
    "vote_delay": 30
}
```

Upvote the posts by [@klye](http://steemit.com/@klye), but not his replies to other posts.
Do not vote if his post is more than 2 hours old.

```
{
    "authors": [
        {"name": "klye"}
    ],
    "max_post_age": "2 hours",
    "vote_key": "5XX...",
    "voter_account_name": "myname"
}
```
