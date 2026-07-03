# MASTERMIND.py (c) 2024 Gregory L. Magnusson MIT license
#
# NOTE: The canonical MASTERMIND implementation has been consolidated into
# mastermind/controller.py (which carries the correct importlib.util/sys
# imports and the full agent lifecycle). This module is retained as a thin
# compatibility shim so that `from mastermind.mastermind import MASTERMIND`
# continues to work; it simply re-exports the canonical implementation.

from mastermind.controller import *  # noqa: F401,F403
from mastermind.controller import AgentInterface, MASTERMIND

__all__ = ["AgentInterface", "MASTERMIND"]

if __name__ == "__main__":
    import logging
    mastermind = MASTERMIND()
    mastermind.execute_agents()
    logging.info("All agents have been executed.")
