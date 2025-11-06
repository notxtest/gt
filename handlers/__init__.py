# ==========================================================
# Group Manager Bot
# Author: notxkrishna (https://github.com/notxkrishnaa) 
# Support: https://t.me/
# Channel: https://t.me/
# License: Private-source (keep credits, no resale)
# ============================================================

from .start import register_handlers



def register_all_handlers(app):
    register_handlers(app)
    
    print("✅ Group commands registered!")
  
