tiny little monte carlo dice simulator with vectorized opperation for speedy output. This has a fairly
natural syntax for expressing multiples of dice, ex:

```python

  roll(4 * D(6))                  # returns a list of 4 random numbers between 1 and 6
  highest(1, roll(D(6) + D(8))    # returns highest 1 number between a D6 and a D8
  
  sum(roll(4 * D(4) + 8))         # sums a 5 entry list with 4 D4 rolls and a bonus of 8
  sum(roll(4 * D(4))) - 8         # sums a 4 entry list of D4 rols then subtracts 8
  
  # to do many rolls simultaneously 
  
  roll(4 * D(6, 1e6))             # rolls 4D6 one million times
  
  histogram(roll(4 * D(6, 1e6)))  # makes a pretty histogram
```

If it switched from using lists to some kind of "Result" class the behavior could be modified to allow subtractors more flexibly.
