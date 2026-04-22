import trio
import httpx
from holehe.core import *
from holehe.modules import *

async def main():
    email = "test@gmail.com"
    out = []
    
    # We can invoke it just to see
    # Well, it's easier to just parse the CSV holehe produces:
    # holehe --only-used --csv email
    pass
