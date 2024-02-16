import shutil

def move_files(location:str =  None):
    
    if not location:
            raise "Give at least one argument. I got None"