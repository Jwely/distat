from pathlib import Path

from classes import *
from serializer import Serializer
from viz import histogram1, RollDefDashboard
from matplotlib import pyplot as plt


adv = RollDef(
    2 * D(20),
    Sum(Highest(1)),
    name='advantage',
    desc='''roll of a d20 with advantage'''
)

disadv = RollDef(
    2 * D(20),
    Sum(Lowest(1)),
    name='disadvantage',
    desc='''roll of a d20 with disadvantage'''
)


atts1 = RollDef(
    RollDef(
        4 * RollDef(
            D(6),
            ReRoll(EqualTo(1))),
        Sum(Highest(3),)),
    ReRoll(LessThan(14)),
    name="very generous 4d6",
    desc=
    '''Generous method of rolling stats for dnd characters.
    Roll 4 D6's and take the highest 3 as the sum. You may reroll 1's,
    but only once. If you are unhappy with a stat, you may repeat the
    process once.''')

atts2 = RollDef(
    4 * RollDef(
        D(6),
        ReRoll(EqualTo(1))),
    Sum(Highest(3),),
    name="generous 4d6",
    desc=
    '''Generous method of rolling stats for dnd characters.
    Roll 4 D6's and take the highest 3 as the sum. You may reroll 1's,
    but only once.''')

atts3 = RollDef(
    4 * D(6),
    Sum(Highest(3)),
    name="4D6, 3 highest, summed",
    desc=
    '''Simplest method of rolling stats for dnd characters.
    Roll 4 D6's and take the sum of the best 3.''')

atts4 = RollDef(
    3 * D(6),
    Sum(),
    name="4D6, 3 highest, summed",
    desc=
    '''Simplest method of rolling stats for dnd characters.
    Roll 4 D6's and take the sum of the best 3.''')

inverse_1 = RollDef(
    D([-1, 1]),
    Sum(),
    name="Inverter",
    desc='''Either -1 or 1 produces pass/fail type scenarios''')


def test_serializer():
    s = Serializer()
    mypath = Path('Dnd_attribute_roll1.json')
    mypath2 = Path('Dnd_attribute_roll2.json')
    mypath3 = Path('Dnd_attribute_roll3.json')

    my_rolldef = atts1   # use example rolldef

    # do the first histogram
    histogram1(my_rolldef(1e6))
    s.dump(my_rolldef, mypath)

    my_rolldef2 = s.load(mypath)
    s.dump(my_rolldef2, mypath2)

    my_rolldef3 = s.load(mypath2)
    s.dump(my_rolldef3, mypath3)

    # second histogram
    histogram1(my_rolldef3(1e6))


def viz_reroll_strat():

    rolldefs = [
        RollDef(
            RollDef(
                4 * RollDef(
                    D(6),
                    ReRoll(EqualTo(1))),
                Sum(Highest(3),)),
            ReRoll(LessThan(i)),
            name=f"RR LT {i}")
        for i in range(9, 17, 1)
        ]

    s = Serializer()
    path = Path("reroll_strat.json")

    #db = RollDefDashboard.from_rolldefs(rolldefs, n=1e4)
    #s.dump(db, path)
    db = s.load(path)
    db.add_accuracy(8e6)
    s.dump(db, path)
    db.show()

if __name__ == "__main__":
    from datetime import datetime

    viz_reroll_strat()


