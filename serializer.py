import simplejson as json
import classes
import viz
import numpy as np

from pathlib import Path
from typing import Dict, Union


CLASS_NAME_KEY = "1_class_name__"
CLASS_ATTRIBUTES_KEY = "2_class_attributes__"


def _to_json(obj: object):
    """
    Converts classes to json.

    All serializable classes must follow a design pattern for this to work!
        1) __init__ args are saved as attributes with identical names, all other
        2) class attributes that are not used as __init__ args must be hidden with '_'

        example:

        class MyClass(object):

            def __init__(arg1, arg2):

                self.arg1 = arg1    # must be named identically to the input arg
                self.arg2 = arg2    # must be named identically to the input arg

                self._arg3 = something  # not used on __init__ so must be hidden
    """
    if hasattr(obj, "__dict__"):
        d = {CLASS_NAME_KEY: obj.__class__.__name__,
             # serialize all class attributes that aren't "hidden" recursively
             CLASS_ATTRIBUTES_KEY: {k: _to_json(v) for k, v in obj.__dict__.items()
                                    if not k.startswith('_')}}
        return d

    if isinstance(obj, list):
        return [_to_json(element) for element in obj]

    if isinstance(obj, tuple):
        return (_to_json(element) for element in obj)

    # special to serialize numpy arrays to lists
    if isinstance(obj, np.ndarray):
        d = {CLASS_NAME_KEY: obj.__class__.__name__,
             CLASS_ATTRIBUTES_KEY: {"object": obj.tolist()}}
        return d
    if isinstance(obj, np.int64):
        return np.asscalar(obj)
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
            classes.Source,
            classes.Die,
            classes.D,
            classes.Filter,
            classes.All,
            classes.Position,
            classes.Highest,
            classes.Lowest,
            classes.Selector,
            classes.EqualTo,
            classes.LessThan,
            classes.GreaterThan,
            classes.Aggregator,
            classes.Sum,
            classes.Difference,
            classes.Action,
            classes.ReRoll,
            classes.RollDef_,
            classes.RollDef,
            classes.Dist,
            viz.RollDefDashboard,
        ]

        self.class_dict = {c.__name__: c for c in class_list}

        # special to deserialize numpy arrays from lists
        self.class_dict.update({"ndarray": np.array})

    @staticmethod
    def dump(obj: object, path: Path = None):
        """ converts object """
        objson = _to_json(obj)
        from pprint import pprint
        pprint(objson)
        dump = json.dumps(objson, indent=4, sort_keys=True)

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
