from pathlib import Path


from classes import RollDef, D, Reroll, Sum, Highest
from serializer import Serializer
from viz import histogram1


def test_serializer():
    s = Serializer()
    mypath = Path('Dnd_attribute_roll1.json')
    mypath2 = Path('Dnd_attribute_roll2.json')
    mypath3 = Path('Dnd_attribute_roll3.json')

    my_rolldef = RollDef(
        4 * D(6, Reroll(1, n_allowed=1)),
        Sum(Highest(3)),
        name="Character creation attribute roll",
        desc=
        '''One common method of rolling stats for dnd characters.
        Roll 4 D6's and take the highest 3 as the sum. You may reroll 1's,
        but only once.''')
    # do the first histogram
    histogram1(my_rolldef(1e5))
    s.dump(my_rolldef, mypath)

    my_rolldef2 = s.load(mypath)
    s.dump(my_rolldef2, mypath2)

    my_rolldef3 = s.load(mypath2)
    s.dump(my_rolldef3, mypath3)

    # second histogram
    histogram1(my_rolldef3(1e5))


if __name__ == "__main__":
    test_serializer()