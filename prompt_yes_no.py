def prompt_yes_no(question, default=None):
    prompt = " (y/n) " if default is None else " (Y/n) " if default else " (y/N) "
    reply = str(input(question + prompt)).lower().strip()
    return (True if reply[:1] == 'y' 
            else False if reply[:1] == 'n' 
            else default if default is not None 
            else prompt_yes_no(question))
