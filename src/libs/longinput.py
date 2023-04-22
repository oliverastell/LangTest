import colorama

def file_input():
    source = ''

    entry = input('>')
    stripped = entry.lstrip()

    if stripped == '':
        return ''

    if stripped[0] == '>':
        print(f"\n{colorama.Fore.YELLOW}TYPE 'exit' TO END{colorama.Style.RESET_ALL}\n 1   {stripped[1:].lstrip()}")
        source = stripped[1:]
        line = 1
        while True:
            line += 1
            entry = input(f" {line}   ")
            if entry == 'exit':
                break
            source += '\n' + entry
    else:
        source = entry
    
    return source