"""Inline keyboard builders."""
from __future__ import annotations

from typing import Iterable, Sequence

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_menu(buttons: Sequence[Sequence[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(list(buttons))


def simple_button(label: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=label, callback_data=callback_data)


def paginated_buttons(
    items: Sequence[InlineKeyboardButton],
    page: int,
    page_size: int,
    back_callback: str,
    extra_buttons: Iterable[InlineKeyboardButton] | None = None,
) -> InlineKeyboardMarkup:
    start = page * page_size
    end = start + page_size
    page_items = items[start:end]
    rows = [[item] for item in page_items]

    nav_row = []
    if start > 0:
        nav_row.append(simple_button("⬅️ Prev", f"page:{page - 1}"))
    if end < len(items):
        nav_row.append(simple_button("Next ➡️", f"page:{page + 1}"))
    if nav_row:
        rows.append(nav_row)

    if extra_buttons:
        rows.extend([[button] for button in extra_buttons])

    rows.append([simple_button("⬅️ Back", back_callback)])
    return build_menu(rows)
