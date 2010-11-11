'''
Various utils
'''

from collections import defaultdict

def parse_command_line_arguments(arguments):
    keyword_parameters = defaultdict(lambda: None)
    parameters = []
    current_key = None

    for argument in arguments[1:]:
        if argument in ('-h', '--host'):
            current_key = 'host'
        else:
            if current_key is not None:
                if argument.startswith('-'):
                    raise Exception('Invalid arguments')
                keyword_parameters[current_key] = argument
                current_key = None
            else:
                parameters.append(argument)
    return parameters, keyword_parameters
