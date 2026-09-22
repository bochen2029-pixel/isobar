"""Direct, file-based adapters: brand-agnostic exports any provider can produce.

mbox / .eml folder (mail) · .ics (calendar) · todo.txt / markdown checklist (list) · .vcf (contacts)
· money.csv (a verdict source, read-only) · the hand lane: a forward address (mbox export or a direct
IMAP mailbox the owner owns) and a paste folder. They emit Observations and never interpret.
"""
from .mbox import MboxConnector
from .ics import IcsConnector
from .textfile import TextListConnector
from .vcf import VcfContacts
from .moneycsv import MoneyCsvVerdict
from .hand import HandMailbox, PasteFolder, parse_forward, network_available

__all__ = ["MboxConnector", "IcsConnector", "TextListConnector", "VcfContacts", "MoneyCsvVerdict",
           "HandMailbox", "PasteFolder", "parse_forward", "network_available"]
