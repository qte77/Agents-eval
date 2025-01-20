"""Redirects to the entrypoint of the app"""

from .app import main
from sys import exit

if __name__ == "__main__":
    exit(main())
