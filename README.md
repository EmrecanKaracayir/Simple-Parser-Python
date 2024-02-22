# Simple-Parser-Python

This GitHub repository contains Python code for implementing LL(1) and LR(1) parsers. It includes functionalities to read LL(1) and LR(1) parsing tables from text files, parse input strings using these tables, and display the parsing process in a tabular format. The code utilizes dataclasses for defining the parsing table structures and provides clear functions for generating and evaluating LL(1) and LR(1) parsing tables.

## Examples

Read LL(1) parsing table from file ll.txt.
Read LR(1) parsing table from file lr.txt.
Read input strings from file input.txt.
Processing input string id+id*id$ for LL(1) parsing table.
NO | STACK | INPUT | ACTION
1 | $ | id+id*id$ | E->TA
2 | $AT | id+id*id$ | T->FB
3 | $ABF | id+id*id$ | F->id
4 | $ABid | id+id*id$ | Match and remove id
5 | $AB | +id*id$ | B->ϵ
6 | $A | +id*id$ | A->+TA
7 | $AT+ | +id*id$ | Match and remove +
8 | $AT | id*id$ | T->FB
9 | $ABF | id*id$ | F->id
10 | $ABid | id*id$ | Match and remove id
11 | $AB | *id$ | B->*FB
12 | $ABF* | *id$ | Match and remove *
13 | $ABF | id$ | F->id
14 | $ABid | id$ | Match and remove id
15 | $AB | $ | B->ϵ
16 | $A | $ | A->ϵ
17 | $ | $ | ACCEPTED
Processing input string acd$ for LR(1) parsing table.
NO | STATE STACK | READ | INPUT | ACTION
1 | 1 | a | acd$ | Shift to state 3
2 | 1 3 | c | acd$ | Shift to state 6
3 | 1 3 6 | d | acd$ | Shift to state 5
4 | 1 3 6 5 | $ | acd$ | Reverse B->d
5 | 1 3 6 | B | acB$ | Shift to state 7
6 | 1 3 6 7 | $ | acB$ | Reverse B->cB
7 | 1 3 | B | aB$ | Shift to state 4
8 | 1 3 4 | $ | aB$ | Reverse S->aB
9 | 1 | S | S$ | Shift to state 2
10 | 1 2 | $ | S$ | ACCEPTED
Processing input string +id*id$ for LL(1) parsing table.
NO | STACK | INPUT | ACTION
1 | $ | +id*id$ | E->TA
2 | $AT | +id*id$ | REJECTED (T does not have an action/step for +)
Processing input string cd$ for LR(1) parsing table.
NO | STATE STACK | READ | INPUT | ACTION
1 | 1 | c | cd$ | REJECTED (State 1 does not have an action/step for c)
