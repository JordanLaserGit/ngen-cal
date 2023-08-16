from contextlib import contextmanager
import sys
import os
from os import getcwd, chdir
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pathlib import Path

@contextmanager
def pushd(path: 'Path') -> None:
    """Change working directory to `path` for duration of the context

    Args:
        path (Path): path to cd to
    """
    #save current working dir
    cwd = getcwd()
    #change to new path
    chdir(path)
    try:
        yield #yield context
    finally:
        #when finished, return to original working dir
        chdir(cwd)
        
def run_args():
    
    if len(sys.argv) > 4:
        ngen_args = sys.argv[1:]
    else:
        ngen_args = []
        ngen_args.append(os.environ.get('CATCH_CONF'))
        ngen_args.append(os.environ.get('CATCH_SUB'))
        ngen_args.append(os.environ.get('NEX_CONF'))
        ngen_args.append(os.environ.get('NEX_SUB'))
        ngen_args.append(os.environ.get('REALIZATION'))
        ngen_args.append(os.environ.get('CROSSWALK'))

    return ngen_args