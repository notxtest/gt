# ==========================================================
# Group Manager Bot
# Author: notxkrishna (https://github.com/notxkrishnaa) 
# Support: https://t.me/
# Channel: https://t.me/
# License: Private-source (keep credits, no resale)
# ============================================================

from .start import register_handlers
from .group_commands import register_group_commands
from .bot_management import register_bot_management


def register_all_handlers(app):
    register_handlers(app)
    register_group_commands(app)
    register_bot_management(app)
    print("✅ Group commands registered!")
  
