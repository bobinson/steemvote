import datetime
import enum
import struct
import time

from piston.steem import Post


class Priority(enum.Enum):
    """Constants for author priority values."""
    low = 'low'
    normal = 'normal'
    high = 'high'
    @classmethod
    def get_index(cls, priority):
        """Get the numeric index of priority."""
        for i, level in enumerate(cls.__members__.values()):
            if level is priority:
                return i

    @classmethod
    def from_index(cls, index):
        """Get the priority at index."""
        for i, level in enumerate(cls.__members__.values()):
            if i == index:
                return level

class User(object):
    """Base class for authors and delegates."""
    @classmethod
    def validate_name(cls, name):
        """Raise if name is invalid."""
        if not name:
            raise ValueError('No name was specified')

    @classmethod
    def validate_priority(cls, priority):
        """Raise if priority is invalid."""
        # This will raise if priority is invalid.
        _ = Priority(priority)

    @classmethod
    def validate_weight(cls, weight):
        """Raise if weight is invalid."""
        if not isinstance(weight, float):
            raise TypeError('A float is required for weight')

class Author(User):
    """An author."""
    def __init__(self, name, vote_replies=False, weight=100.0, priority=Priority.normal):
        self.validate_name(name)
        self.validate_weight(weight)
        self.validate_priority(priority)

        self.name = name
        self.vote_replies = vote_replies
        self.weight = weight
        self.priority = priority

    @classmethod
    def from_config(cls, value):
        """Instantiate from config value."""
        if isinstance(value, dict):
            return cls.from_dict(value)
        elif isinstance(value, str):
            return cls(name=value)
        elif isinstance(value, bytes):
            return cls(name=str(value, 'utf-8'))
        else:
            raise TypeError('A string or dict is required')

    @classmethod
    def from_dict(cls, d):
        name = d.get('name')
        vote_replies = d.get('vote_replies', False)
        weight = d.get('weight', 100.0)
        priority = Priority(d.get('priority', 'normal'))
        return cls(name, vote_replies=vote_replies, weight=weight, priority=priority)

    def to_dict(self):
        return {
            'name': self.name,
            'vote_replies': self.vote_replies,
            'weight': self.weight,
            'priority': self.priority.value,
        }

class Delegate(User):
    """A delegate voter."""
    def __init__(self, name, weight=100.0, priority=Priority.normal):
        self.validate_name(name)
        self.validate_weight(weight)
        self.validate_priority(priority)

        self.name = name
        self.weight = weight
        self.priority = priority

    @classmethod
    def from_config(cls, value):
        """Instantiate from config value."""
        if isinstance(value, dict):
            return cls.from_dict(value)
        elif isinstance(value, str):
            return cls(name=value)
        elif isinstance(value, bytes):
            return cls(name=str(value, 'utf-8'))
        else:
            raise TypeError('A string or dict is required')

    @classmethod
    def from_dict(cls, d):
        name = d.get('name')
        weight = d.get('weight', 100.0)
        priority = Priority(d.get('priority', 'normal'))
        return cls(name, weight=weight, priority=priority)

    def to_dict(self):
        return {
            'name': self.name,
            'weight': self.weight,
            'priority': self.priority.value,
        }

class Comment(Post):
    """A comment."""
    def __init__(self, steem, post):
        super(Comment, self).__init__(steem, post)
        self.timestamp = int(self.created_parsed.replace(tzinfo=datetime.timezone.utc).timestamp())

    def is_reply(self):
        return True if self.parent_author else False

    def get_url(self, domain='https://steemit.com'):
        """Get the URL for this comment at domain."""
        domain = domain.rstrip('/')
        return domain + self.url

    def get_have_voted(self, voter_names):
        """Get the names in voter_names that have voted for this comment."""
        active_voters = [d['voter'] for d in self.active_votes]
        result = set(voter_names).intersection(set(active_voters))
        return list(result)
