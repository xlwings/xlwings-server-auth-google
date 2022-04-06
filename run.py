"""
This is for local development only. You could also run the following from the
command line instead (run from the root directory):

uvicorn app.main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
