import simplejson as json
import classes
import bases
from pathlib import Path
from typing import Dict, Union


CLASS_NAME_KEY = "1_class_name__"
CLASS_ATTRIBUTES_KEY = "2_class_attributes__"


def _to_json(obj: object):
    """ converts classes to json """
    if hasattr(obj, "__dict__"):
        d = {CLASS_NAME_KEY: obj.__class__.__name__,
             CLASS_ATTRIBUTES_KEY: {k: _to_json(v) for k, v in obj.__dict__.items()}}
        return d

    if isinstance(obj, list):
        return [_to_json(element) for element in obj]

    if isinstance(obj, tuple):
        return (_to_json(element) for element in obj)

    else:
        return obj


def _from_json(obj: object, class_dict: Dict):
    """
    reads dictionaries containing data about distat classes and turns them
    into class instances
    """

    def is_class_dict(d):
        if isinstance(d, dict):
            if CLASS_NAME_KEY in d.keys() and CLASS_ATTRIBUTES_KEY in d.keys():
                return True
        return False

    if is_class_dict(obj):
        cls = class_dict[obj[CLASS_NAME_KEY]]
        args = obj[CLASS_ATTRIBUTES_KEY]
        recursive_args = {k: _from_json(v, class_dict) for k, v in args.items()}
        return cls(**recursive_args)

    elif isinstance(obj, list):
        return [_from_json(element, class_dict) for element in obj]

    elif isinstance(obj, tuple):
        return (_from_json(element, class_dict) for element in obj)

    else:
        return obj


class Serializer(object):
    """
    Based on a fairly simple method of turning every distat
    class into a dictionary with two keys defined by the
    CLASS_NAME_KEY and CLASS_ATTRIBUTES_KEY globals, this
    class will json serialize instances of all distat classes and
    load them again.
    """
    def __init__(self):

        # TODO: this is a list of supported classes that can be deserialized
        class_list = [
            bases.Die_,
            bases.Rule_,
            bases.Selector_,
            bases.Aggregator_,
            bases.Sum_,
            classes.Modifier,
            classes.Die,
            classes.D,
            classes.Maximize,
            classes.Reroll,
            classes.Pool,
            classes.Selector,
            classes.Aggregator,
            classes.Sum,
            classes.Highest,
            classes.Lowest,
            classes.Pos,
            classes.RollDef
        ]

        self.class_dict = {c.__name__: c for c in class_list}

    @staticmethod
    def dump(obj: object, path: Path = None):
        """ converts object """
        dump = json.dumps(_to_json(obj), indent=4, sort_keys=True)

        if path is not None:
            with open(path, 'w+') as f:
                f.write(dump)

        return dump

    def load(self, s: Union[str, Path]):
        """ reads a json string or file """
        if isinstance(s, Path):
            with open(s, 'r') as f:
                s = f.read()

        load = _from_json(json.loads(s), self.class_dict)
        return load
