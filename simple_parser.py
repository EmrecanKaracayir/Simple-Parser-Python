'''
@authors
  - Emrecan Karacayir
'''
import copy
import sys
import unicodedata
from dataclasses import dataclass

# FILE CONSTANTS
FILE_LL: str = "ll.txt"
FILE_LR: str = "lr.txt"
FILE_INPUT: str = "input.txt"

# OPERATION CONSTANTS
ID_SYMBOL: str = "#"

# NECESSARY OBJECTS
@dataclass
class LL:
    '''
    Represents an LL(1) parsing table.

    Attributes
    ----------
    start_symbol : str
        The starting non-terminal symbol of the grammar.
    start_rule : str
        The production rule for the starting symbol.
    table : dict[str, dict[str, str]]
        A dictionary representing the LL(1) parsing table. The keys of the outer dictionary are non-terminals,
        and the values are dictionaries that map terminals to production rules.
    '''
    start_symbol: str
    start_rule: str
    table: dict[str, dict[str, str]]

@dataclass
class LR:
    '''
    Represents an LR(1) parsing table.

    Attributes
    ----------
    start_state : str
        The starting state for the evaluation.
    table : dict[str, dict[str, str]]
        A dictionary representing the LR(1) parsing table. The keys of the outer dictionary are states,
        and the values are dictionaries that map states to actions/steps.
    '''
    start_state: str
    table: dict[str, dict[str, str]]

@dataclass
class ParsingInput:
    '''
    Represents an input string and the parsing method to use for that string.

    Attributes
    ----------
    method : str
        The parsing method to use for the input string. Valid values are "LL" and "LR".
    string : str
        The input string to parse.
    '''
    method: str
    string: str

def read(file_to_read: str) -> list[str]:
    '''
    Reads the contents of a file, removes control characters, and returns a list of lines.

    Parameters
    ----------
    file_to_read : str
        The name of the file to read (must be in the same directory).

    Returns
    -------
    list[str]
        A list of strings representing the lines of the file.

    Raises
    ------
    FileNotFoundError
        If the file with the given name is not found in the current directory.
    '''
    try:
        with open(file=file_to_read, mode="r", encoding="UTF-8") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                lines[i] = "".join(c for c in line.replace(" ", "") if unicodedata.category(c)[0] != 'C')
            return lines
    except FileNotFoundError:
        print(f"[FAIL] | \"{file_to_read}\" does not exist in the current directory.")
        sys.exit(1)

def generate_ll_table(contents: list[str]) -> LL:
    '''
    Parses the contents of an LL(1) parsing table file and returns a dictionary representing the table.

    Parameters
    ----------
    contents : list[str]
        A list of strings representing the lines of the file.

    Returns
    -------
    LL
        An LL object representing the LL(1) parsing table. The object has attributes for the start symbol,
        the start rule, and the parsing table itself.
    '''
    for i, line in enumerate(contents):
        contents[i] = line.replace("id", ID_SYMBOL)
    ll_start_symbol: str = ""
    ll_start_rule: str = ""
    ll_start_rule_found: bool = False
    ll_table: dict[str, dict[str, str]] = {}
    terminals: list[str] = contents[0].split(';')[1:]
    for line in contents[1:]:
        tokens: list[str] = line.split(';')
        non_terminal: str = tokens[0]
        productions: dict[str, str] = {}
        for i, token in enumerate(tokens[1:]):
            if token != '':
                token = token.replace(f"{non_terminal}->", "")
                productions[terminals[i]] = token
                if not ll_start_rule_found:
                    ll_start_symbol = non_terminal
                    ll_start_rule = token
                    ll_start_rule_found = True
        ll_table[non_terminal] = productions
    return LL(ll_start_symbol, ll_start_rule, ll_table)

def generate_lr_table(contents: list[str]) -> LR:
    '''
    Parses the contents of an LR(1) parsing table file and returns a dictionary representing the table.

    Parameters
    ----------
    contents : list[str]
        A list of strings representing the lines of the file.

    Returns
    -------
    LR
        An LR object representing the LR(1) parsing table. The object has attributes for the start state, 
        and the parsing table itself.
    '''
    lr_start_state: str = ""
    lr_start_state_found: bool = False
    lr_table: dict[str, dict[str, str]] = {}
    cond_symbols: list[str] = contents[1].split(';')[1:]
    for line in contents[2:]:
        tokens: list[str] = line.split(';')
        state: str = tokens[0]
        if not lr_start_state_found:
            lr_start_state = state
            lr_start_state_found = True
        actions: dict[str, str] = {}
        for i, token in enumerate(tokens[1:]):
            if token != '':
                actions[cond_symbols[i]] = token
        lr_table[state] = actions
    return LR(lr_start_state, lr_table)

def generate_parsing_inputs(contents: list[str]) -> list[ParsingInput]:
    '''
    Parse the contents of an input file and return a list of ParsingInput objects.

    Parameters
    ----------
    contents : list[str]
        A list of strings representing the lines of the file.

    Returns
    -------
    list[ParsingInput]
        A list of ParsingInput objects. Each object represents an input string and the parsing method to use
        for that string.
    '''
    parsing_inputs: list[ParsingInput] = []
    for line in contents[1:]:
        tokens: list[str] = line.split(';')
        match tokens[0]:
            case "LL":
                parsing_inputs.append(ParsingInput("LL", tokens[1]))
            case "LR":
                parsing_inputs.append(ParsingInput("LR", tokens[1]))
            case _:
                print(f"[WARN] | Unsupported parsing method \"{tokens[0]}\" found in the file \"{FILE_INPUT}\" and ignored.")
    return parsing_inputs

def evaluate_ll_input(ll: LL, input: str) -> list[dict[str, str]]:
    '''
    Evaluates an input string using an LL(1) parsing table.

    Parameters
    ----------
    ll : LL
        An LL object representing the LL(1) parsing table.
    input : str
        The input string to evaluate.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries representing the steps taken during the evaluation of the input string.
        Each dictionary has the keys "STEP", "ACTION", "STACK", and "INPUT", which represent the step number,
        the production rule or reduction applied, the current stack state, and the current input queue, respectively.
    '''
    print()
    print(f"[INFO] | Processing input string \"{input}\" for LL(1) parsing table.")
    input = input.replace("id", ID_SYMBOL)
    outputs: list[dict[str, str]] = []
    queue: list[str] = [symbol for symbol in input]
    stack: list[str] = []
    stack.append("$")
    step_counter: int = 1
    evaluation_finished: bool = False
    while not evaluation_finished:
        output: dict[str, str] = {}
        temp_stack = copy.deepcopy(stack)
        temp_queue = copy.deepcopy(queue)
        if step_counter == 1:
            output["ACTION"] = f"{ll.start_symbol}->{ll.start_rule}"
            for symbol in reversed(ll.start_rule):
                temp_stack.append(symbol)
        else:
            stack_item = temp_stack.pop()
            queue_item = temp_queue[0]
            if stack_item == "$" and queue_item == "$":
                output["ACTION"] = "ACCEPTED"
                evaluation_finished = True
            else:
                if stack_item == queue_item:
                    temp_queue.remove(queue_item)
                    output["ACTION"] = f"Match and remove \"{queue_item}\""
                else:
                    productions = ll.table.get(stack_item)
                    if productions is not None:
                        production = productions.get(queue_item)
                        if production is not None:
                            output["ACTION"] = f"\"{stack_item}->{production}\""
                            if production != "ϵ":
                                for symbol in reversed(production):
                                    temp_stack.append(symbol)
                        else:
                            output["ACTION"] = f"REJECTED (\"{stack_item}\" doesn't have an action/step for \"{queue_item}\")"
                            evaluation_finished = True
                    else:
                        output["ACTION"] = f"REJECTED (\"{stack_item}\" not found in LL(1) parsing table)"
                        evaluation_finished = True
        output["NO"] = str(step_counter)
        output["STACK"] = "".join(stack)
        output["INPUT"] = "".join(queue)
        outputs.append(output)
        stack = copy.deepcopy(temp_stack)
        queue = copy.deepcopy(temp_queue)
        step_counter += 1
    return outputs

def evaluate_lr_input(lr: LR, input: str) -> list[dict[str, str]]:
    '''
    Evaluates an input string using an LR(1) parsing table.

    Parameters
    ----------
    lr : LR
        An LR object representing the LR(1) parsing table.
    input : str
        The input string to evaluate.

    Returns
    -------
    list[dict[str, str]]
        A list of dictionaries representing the steps taken during the evaluation of the input string.
        Each dictionary has the keys "STEP", "ACTION", "STATE STACK", and "INPUT", which represent the step number,
        the production rule or reduction applied, the current state stack state, and the current input queue, respectively.
    '''
    print()
    print(f"[INFO] | Processing input string \"{input}\" for LR(1) parsing table.")
    outputs: list[dict[str, str]] = []
    compounds: list[dict[str, str]] = []
    compounds.append({"state": lr.start_state, "symbol": ""})
    for symbol in input:
        compounds.append({"symbol": symbol})
    step_counter: int = 1
    evaluation_finished: bool = False
    while not evaluation_finished:
        output: dict[str, str] = {}
        temp_compounds = copy.deepcopy(compounds)
        for i, temp_compound in enumerate(temp_compounds):
            if temp_compound.get("state") is None:
                symbol = temp_compound.get("symbol")
                if symbol is not None:
                    output["READ"] = symbol
                    prev_state = temp_compounds[i-1].get("state")
                    if prev_state is not None:
                        prev_state_actions = lr.table.get(prev_state)
                        if prev_state_actions is not None:
                            prev_state_action = prev_state_actions.get(symbol)
                            if prev_state_action is not None:
                                if prev_state_action.lower() == "accept":
                                    output["ACTION"] = "ACCEPTED"
                                    evaluation_finished = True
                                    break
                                elif prev_state_action.startswith("State_"):
                                    output["ACTION"] = f"Shift to \"{prev_state_action}\""
                                    temp_compound["state"] = prev_state_action
                                    break
                                elif "->" in prev_state_action:
                                    output["ACTION"] = f"Reverse \"{prev_state_action}\""
                                    symbols_to_delete = list(prev_state_action[3:])
                                    compounds_to_delete: list[dict[str, str]] = []
                                    action_is_valid: bool = True
                                    for j in range(1, len(symbols_to_delete) + 1):
                                        temp_symbol = temp_compounds[i - j].get("symbol")
                                        if temp_symbol is not None:
                                            if temp_symbol != symbols_to_delete[len(symbols_to_delete) - j]:
                                                action_is_valid = False
                                                break
                                            else:
                                                compounds_to_delete.append(temp_compounds[i - j])
                                        else:
                                            output["ACTION"] = "REJECTED (Previous symbol not found in compounds)"
                                            evaluation_finished = True
                                            break
                                    if action_is_valid:
                                        temp_compounds = [compound for compound in temp_compounds if compound not in compounds_to_delete]
                                        temp_compounds.insert(len(temp_compounds) - 1, {"symbol": prev_state_action[0]})
                                    break
                                else:
                                    output["ACTION"] = f"REJECTED (Incorrect action/step for \"{symbol}\" in \"State_{prev_state.replace('State_', '')}\")"
                                    evaluation_finished = True
                                    break
                            else:
                                output["ACTION"] = f"REJECTED (\"State_{prev_state.replace('State_', '')}\" does not have an action/step for \"{symbol}\")"
                                evaluation_finished = True
                                break
                        else:
                            output["ACTION"] = "REJECTED (Previous state actions/steps not found in LR(1) table)"
                            evaluation_finished = True
                            break  
                    else:
                        output["ACTION"] = "REJECTED (Previous state not found in compounds)"
                        evaluation_finished = True
                        break
                else:
                    output["ACTION"] = f"REJECTED (\"{symbol}\" not found in compounds)"
                    evaluation_finished = True
                    break
            else:
                continue
        output["NO"] = str(step_counter)
        state_stack_list: list[str] = []
        input_stack_list: list[str] = []
        for compound in compounds:
            state = compound.get("state")
            if state is not None:
                state_stack_list.append(state.replace("State_", ""))
            symbol = compound.get("symbol")
            if symbol is not None:
                input_stack_list.append(symbol)
            else:
                output["ACTION"] = "REJECTED (One or more symbols missing in compounds)"
                evaluation_finished = True
                break
        output["STATE STACK"] = "".join(list(' '.join(state_stack_list)))
        output["INPUT"] = "".join(input_stack_list)
        outputs.append(output)
        compounds = copy.deepcopy(temp_compounds)
        step_counter += 1
    return outputs
    
def display_ll_table_outputs(outputs: list[dict[str, str]]):
    '''
    Displays the outputs of the LL(1) parsing table evaluation in a tabular format.

    Parameters
    ----------
    outputs : list[dict[str, str]]
        A list of dictionaries representing the steps taken during the evaluation of the input string.
        Each dictionary has the keys "NO", "STACK", "INPUT", and "ACTION", which represent the step number,
        the current stack state, the current input queue, and the production rule or reduction applied, respectively.

    Returns
    -------
    None
    '''
    print()
    no_col_max_len: int = 0
    stack_col_max_len: int = 0
    input_col_max_len: int = 0
    for output in outputs:
        no_col = output.get("NO")
        if no_col is not None:
            no_col = no_col
            no_col_max_len = len(no_col) if no_col_max_len < len(no_col) else no_col_max_len
        stack_col = output.get("STACK")
        if stack_col is not None:
            stack_col = stack_col.replace(ID_SYMBOL, "id")
            stack_col_max_len = len(stack_col) if stack_col_max_len < len(stack_col) else stack_col_max_len
        input_col = output.get("INPUT")
        if input_col is not None:
            input_col = input_col.replace(ID_SYMBOL, "id")
            input_col_max_len = len(input_col) if input_col_max_len < len(input_col) else input_col_max_len
    print(f"NO{' ' * (no_col_max_len - len('NO'))} | STACK{' ' * (stack_col_max_len - len('STACK'))} | INPUT{' ' * (input_col_max_len - len('INPUT'))} | ACTION")
    for output in outputs:
        no_out = output.get("NO")
        stack_out = output.get("STACK")
        input_out = output.get("INPUT")
        action_out = output.get("ACTION")
        if no_out is not None and stack_out is not None and input_out is not None and action_out is not None:
            no_out = no_out.replace(ID_SYMBOL, "id")
            stack_out = stack_out.replace(ID_SYMBOL, "id")
            input_out = input_out.replace(ID_SYMBOL, "id")
            action_out = action_out.replace(ID_SYMBOL, "id")
            print(f"{no_out}{' ' * max((len('NO') - len(no_out)), (no_col_max_len - len(no_out)))} | {stack_out}{' ' * max((len('STACK') - len(stack_out)), (stack_col_max_len - len(stack_out)))} | {' ' * max((len('INPUT') - len(input_out)), (input_col_max_len - len(input_out)))}{input_out} | {action_out}")

def display_lr_table_outputs(outputs: list[dict[str, str]]):
    '''
    Displays the outputs of the LR(1) parsing table evaluation in a tabular format.

    Parameters
    ----------
    outputs : list[dict[str, str]]
        A list of dictionaries representing the steps taken during the evaluation of the input string.
        Each dictionary has the keys "NO", "STATE STACK", "READ", INPUT", and "ACTION", which represent the step number,
        the current state stack state, the read symbol, the current input queue, and the production rule or reduction 
        applied, respectively.

    Returns
    -------
    None
    '''
    print()
    no_col_max_len: int = 0
    stack_col_max_len: int = 0
    input_col_max_len: int = 0
    for output in outputs:
        no_col = output.get("NO")
        if no_col is not None:
            no_col_max_len = len(no_col) if no_col_max_len < len(no_col) else no_col_max_len
        stack_col = output.get("STATE STACK")
        if stack_col is not None:
            stack_col_max_len = len(stack_col) if stack_col_max_len < len(stack_col) else stack_col_max_len
        input_col = output.get("INPUT")
        if input_col is not None:
            input_col_max_len = len(input_col) if input_col_max_len < len(input_col) else input_col_max_len
    print(f"NO{' ' * (no_col_max_len - len('NO'))} | STATE STACK{' ' * (stack_col_max_len - len('STATE STACK'))} | READ | INPUT{' ' * (input_col_max_len - len('INPUT'))} | ACTION")
    for output in outputs:
        no_out = output.get("NO")
        stack_out = output.get("STATE STACK")
        read_out = output.get("READ")
        input_out = output.get("INPUT")
        action_out = output.get("ACTION")
        if no_out is not None and stack_out is not None and input_out is not None and action_out is not None:
            no_out = no_out
            stack_out = stack_out
            input_out = input_out
            action_out = action_out
            print(f"{no_out}{' ' * max((len('NO') - len(no_out)), (no_col_max_len - len(no_out)))} | {stack_out}{' ' * max((len('STATE STACK') - len(stack_out)), (stack_col_max_len - len(stack_out)))} | {read_out}    | {' ' * max((len('INPUT') - len(input_out)), (input_col_max_len - len(input_out)))}{input_out} | {action_out}")

def main():
    ll: LL = generate_ll_table(read(FILE_LL))
    print(f"[INFO] | Read LL(1) parsing table from file \"{FILE_LL}\".")

    lr: LR = generate_lr_table(read(FILE_LR))
    print(f"[INFO] | Read LR(1) parsing table from file \"{FILE_LR}\".")

    parsing_inputs: list[ParsingInput] = generate_parsing_inputs(read(FILE_INPUT))
    print(f"[INFO] | Read input strings from file \"{FILE_INPUT}\".")

    while len(parsing_inputs) > 0:
        parsing_input: ParsingInput = parsing_inputs.pop(0)
        match parsing_input.method:
            case "LL":
                display_ll_table_outputs(evaluate_ll_input(ll, parsing_input.string))
            case "LR":
                display_lr_table_outputs(evaluate_lr_input(lr, parsing_input.string))
            case _:
                print(f"[WARN] | Unexpected parsing method \"{parsing_input.method}\" found and ignored.")
        
main()
