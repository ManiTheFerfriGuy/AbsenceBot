"""Telegram bot handlers for AbsenceBot."""
from __future__ import annotations

import logging
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Iterable, List, Optional

from telegram import InlineKeyboardButton, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from absence_bot.config import BotConfig
from absence_bot.database import Database, session_scope
from absence_bot.keyboards import build_menu, paginated_buttons, simple_button
from absence_bot.models import Absence, AuthorizedTeacher, Grade, Major, Student

LOGGER = logging.getLogger(__name__)

STATE_ADDING_STUDENTS = "adding_students"
STATE_ABSENCE_SELECTION = "absence_selection"
STATE_ADDING_GRADE = "adding_grade"
STATE_ADDING_MAJOR = "adding_major"
STATE_ADDING_TEACHER = "adding_teacher"
STATE_EDITING_GRADE = "editing_grade"
STATE_EDITING_MAJOR = "editing_major"
STATE_EDITING_STUDENT = "editing_student"
STATE_GRADE = "selected_grade"
STATE_MANAGE_GRADES = "manage_grades"
STATE_MANAGE_MAJORS = "manage_majors"
STATE_MANAGE_STUDENTS = "manage_students"
STATE_MAJOR = "selected_major"
STATE_PAGE = "page"
STATE_SELECTED_STUDENTS = "selected_students"


@dataclass
class HandlerContext:
    config: BotConfig
    database: Database


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        return
    handler_context: HandlerContext = context.bot_data["handler_context"]
    if not _is_authorized(update.effective_user.id, handler_context):
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return

    await _show_main_menu(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    handler_context: HandlerContext = context.bot_data["handler_context"]
    if not _is_authorized(update.effective_user.id, handler_context):
        await update.message.reply_text("🚫 You are not authorized to use this bot.")
        return

    if context.user_data.get(STATE_ADDING_STUDENTS):
        try:
            await _handle_student_input(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling student input: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_ADDING_GRADE):
        if not _is_management(update.effective_user.id, handler_context.config):
            await update.message.reply_text("🚫 You are not authorized to manage grades.")
            context.user_data.pop(STATE_ADDING_GRADE, None)
            return
        try:
            await _handle_grade_input(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling grade input: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_EDITING_GRADE):
        if not _is_management(update.effective_user.id, handler_context.config):
            await update.message.reply_text("🚫 You are not authorized to manage grades.")
            context.user_data.pop(STATE_EDITING_GRADE, None)
            return
        try:
            await _handle_grade_edit(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling grade edit: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_ADDING_MAJOR):
        try:
            await _handle_major_input(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling major input: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_EDITING_MAJOR):
        if not _is_management(update.effective_user.id, handler_context.config):
            await update.message.reply_text("🚫 You are not authorized to manage majors.")
            context.user_data.pop(STATE_EDITING_MAJOR, None)
            return
        try:
            await _handle_major_edit(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling major edit: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_EDITING_STUDENT):
        if not _is_management(update.effective_user.id, handler_context.config):
            await update.message.reply_text("🚫 You are not authorized to manage students.")
            context.user_data.pop(STATE_EDITING_STUDENT, None)
            return
        try:
            await _handle_student_edit(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling student edit: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return
    if context.user_data.get(STATE_ADDING_TEACHER):
        if not _is_management(update.effective_user.id, handler_context.config):
            await update.message.reply_text("🚫 You are not authorized to manage teachers.")
            context.user_data.pop(STATE_ADDING_TEACHER, None)
            return
        try:
            await _handle_teacher_input(update, context, handler_context)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Error handling teacher input: %s", exc)
            await update.message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        return

    await update.message.reply_text("Please use the inline menu below.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    handler_context: HandlerContext = context.bot_data["handler_context"]
    if not _is_authorized(update.effective_user.id, handler_context):
        await update.callback_query.answer("Unauthorized", show_alert=True)
        return

    data = update.callback_query.data or ""
    await update.callback_query.answer()

    try:
        if data == "noop":
            return
        if data == "menu:main":
            context.user_data.clear()
            await _show_main_menu(update, context)
            return
        if data == "menu:data":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to access data tools."
                )
                return
            context.user_data.clear()
            await _show_data_menu(update, context)
            return
        if data == "menu:students":
            context.user_data.clear()
            await _show_student_menu(update, context)
            return
        if data == "menu:majors":
            context.user_data.clear()
            context.user_data[STATE_MANAGE_MAJORS] = "students"
            await _prompt_grade(
                update,
                context,
                title="Select grade to manage majors",
                back_target="menu:students",
            )
            return
        if data == "data:students":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage student data."
                )
                return
            context.user_data.clear()
            await _show_data_students_menu(update, context)
            return
        if data == "data:students_manage":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage student data."
                )
                return
            context.user_data.clear()
            context.user_data[STATE_MANAGE_STUDENTS] = True
            await _prompt_grade(update, context, title="Select grade to manage students", back_target="data:students")
            return
        if data == "data:majors":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage majors."
                )
                return
            context.user_data.clear()
            context.user_data[STATE_MANAGE_MAJORS] = "data"
            await _prompt_grade(
                update,
                context,
                title="Select grade to manage majors",
                back_target="menu:data",
            )
            return
        if data == "data:grades":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage grades."
                )
                return
            context.user_data.clear()
            context.user_data[STATE_MANAGE_GRADES] = True
            await _show_grade_management(update, context)
            return
        if data == "menu:management":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to access management tools."
                )
                return
            context.user_data.clear()
            await _show_management_menu(update, context)
            return
        if data == "menu:absence":
            context.user_data.clear()
            await _start_absence_flow(update, context)
            return
        if data.startswith("students:add"):
            await _start_add_students(update, context)
            return
        if data.startswith("students:view"):
            await _start_view_students(update, context)
            return
        if data.startswith("grade:"):
            await _handle_grade_selection(update, context, data.split(":", 1)[1])
            return
        if data == "major:add":
            await _start_add_major(update, context)
            return
        if data.startswith("major:edit:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to edit majors."
                )
                return
            await _start_edit_major(update, context, data.split(":", 2)[2])
            return
        if data.startswith("major:delete:"):
            await _delete_major(update, context, data.split(":", 2)[2])
            return
        if data.startswith("major:select:"):
            await _handle_major_selection(update, context, data.split(":", 2)[2])
            return
        if data.startswith("page:"):
            await _handle_page(update, context, int(data.split(":", 1)[1]))
            return
        if data.startswith("absence:toggle:"):
            await _toggle_absence_student(update, context, data.split(":", 2)[2])
            return
        if data == "absence:confirm":
            await _confirm_absences(update, context, handler_context)
            return
        if data == "absence:cancel":
            await _start_absence_flow(update, context)
            return
        if data == "management:export":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to export the database."
                )
                return
            await update.callback_query.edit_message_text(
                "Preparing database export..."
            )
            await _send_database_backup(
                context,
                handler_context,
                update.effective_user.id,
                "📦 Manual database export",
            )
            await _show_management_menu(update, context)
            return
        if data == "management:add_teacher":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage teachers."
                )
                return
            context.user_data.clear()
            context.user_data[STATE_ADDING_TEACHER] = True
            keyboard = build_menu([[simple_button("⬅️ Cancel", "menu:management")]])
            await update.callback_query.edit_message_text(
                "Send the teacher's Telegram user ID (numbers only).",
                reply_markup=keyboard,
            )
            return
        if data == "grade:add":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage grades."
                )
                return
            await _start_add_grade(update, context)
            return
        if data.startswith("grade:delete:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage grades."
                )
                return
            await _delete_grade(update, context, data.split(":", 2)[2])
            return
        if data.startswith("grade:edit:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage grades."
                )
                return
            await _start_edit_grade(update, context, data.split(":", 2)[2])
            return
        if data.startswith("student:manage:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage students."
                )
                return
            await _show_student_management_actions(update, context, data.split(":", 2)[2])
            return
        if data.startswith("student:edit:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage students."
                )
                return
            await _start_edit_student(update, context, data.split(":", 2)[2])
            return
        if data.startswith("student:delete:"):
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage students."
                )
                return
            await _delete_student(update, context, data.split(":", 2)[2])
            return
        if data == "students:manage":
            if not _is_management(update.effective_user.id, handler_context.config):
                await update.callback_query.edit_message_text(
                    "🚫 You are not authorized to manage students."
                )
                return
            await _show_student_management_list(update, context)
            return
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Error handling callback: %s", exc)
        await update.callback_query.edit_message_text(
            "An unexpected error occurred. Please try again or contact support."
        )
        return

    await update.callback_query.edit_message_text("Invalid action. Please use the menu.")


async def _show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    show_management = (
        update.effective_user
        and _is_management(update.effective_user.id, handler_context.config)
    )
    keyboard = build_menu(
        [
            [simple_button("📚 Manage Students", "menu:students")],
            [simple_button("📝 Record Absence", "menu:absence")],
            *(
                [
                    [simple_button("🗂️ Data", "menu:data")],
                    [simple_button("🛠️ Management", "menu:management")],
                ]
                if show_management
                else []
            ),
        ]
    )
    if update.message:
        await update.message.reply_text("Welcome! Choose an option:", reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text("Main Menu:", reply_markup=keyboard)


async def _show_student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_menu(
        [
            [simple_button("➕ Add Students", "students:add")],
            [simple_button("📋 View Students", "students:view")],
            [simple_button("🗂️ Manage Majors", "menu:majors")],
            [simple_button("⬅️ Back", "menu:main")],
        ]
    )
    await update.callback_query.edit_message_text("Student Management:", reply_markup=keyboard)


async def _show_data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_menu(
        [
            [simple_button("👥 Students", "data:students")],
            [simple_button("🎓 Grades", "data:grades")],
            [simple_button("🧭 Majors", "data:majors")],
            [simple_button("⬅️ Back", "menu:main")],
        ]
    )
    await update.callback_query.edit_message_text("Data Management:", reply_markup=keyboard)


async def _show_data_students_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_menu(
        [
            [simple_button("➕ Add Students", "students:add")],
            [simple_button("✏️ Edit/Delete Students", "data:students_manage")],
            [simple_button("⬅️ Back", "menu:data")],
        ]
    )
    await update.callback_query.edit_message_text("Student Data:", reply_markup=keyboard)


async def _show_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_menu(
        [
            [simple_button("📤 Export Database", "management:export")],
            [simple_button("➕ Add Teacher ID", "management:add_teacher")],
            [simple_button("⬅️ Back", "menu:main")],
        ]
    )
    if update.callback_query:
        await update.callback_query.edit_message_text("Management Tools:", reply_markup=keyboard)
    else:
        await update.message.reply_text("Management Tools:", reply_markup=keyboard)


async def _start_add_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data[STATE_ADDING_STUDENTS] = True
    await _prompt_grade(update, context, title="Select grade to add students")


async def _start_view_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await _prompt_grade(update, context, title="Select grade to view students")


async def _start_absence_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data[STATE_ABSENCE_SELECTION] = True
    await _prompt_grade(update, context, title="Select grade for absence")


async def _prompt_grade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    title: str,
    back_target: str = "menu:main",
) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grades = _fetch_grades(handler_context)
    if not grades:
        await update.callback_query.edit_message_text(
            "No grades configured yet. Ask a manager to add grades first.",
            reply_markup=build_menu([[simple_button("⬅️ Back", back_target)]]),
        )
        return
    rows = [[simple_button(grade, f"grade:{grade}")] for grade in grades]
    rows.append([simple_button("⬅️ Back", back_target)])
    keyboard = build_menu(rows)
    await update.callback_query.edit_message_text(title, reply_markup=keyboard)


async def _handle_grade_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, grade: str
) -> None:
    context.user_data[STATE_GRADE] = grade
    context.user_data[STATE_PAGE] = 0

    if context.user_data.get(STATE_MANAGE_MAJORS):
        await _show_major_management(update, context)
        return

    handler_context: HandlerContext = context.bot_data["handler_context"]
    majors = _fetch_majors(handler_context, grade)
    if not majors:
        back_target = "data:students" if context.user_data.get(STATE_MANAGE_STUDENTS) else "menu:main"
        await update.callback_query.edit_message_text(
            "No majors configured for this grade. Use Manage Majors to add them.",
            reply_markup=build_menu([[simple_button("⬅️ Back", back_target)]]),
        )
        return

    rows = [[simple_button(major, f"major:select:{major}")] for major in majors]
    rows.append([simple_button("⬅️ Back", "menu:main")])
    keyboard = build_menu(rows)
    await update.callback_query.edit_message_text("Select major:", reply_markup=keyboard)


def _fetch_majors(handler_context: HandlerContext, grade: str) -> list[str]:
    with session_scope(handler_context.database) as session:
        majors = (
            session.query(Major)
            .filter(Major.grade == grade)
            .order_by(Major.name.asc())
            .all()
        )
    return [major.name for major in majors]


def _fetch_grades(handler_context: HandlerContext) -> list[str]:
    with session_scope(handler_context.database) as session:
        grades = session.query(Grade).order_by(Grade.name.asc()).all()
    if grades:
        return [grade.name for grade in grades]
    return handler_context.config.grades


async def _show_major_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grade = context.user_data.get(STATE_GRADE)
    if not grade:
        await update.callback_query.edit_message_text("Please select a grade first.")
        return

    show_edit = bool(
        update.effective_user
        and _is_management(update.effective_user.id, handler_context.config)
    )
    majors = _fetch_majors(handler_context, grade)
    rows = []
    if majors:
        for major in majors:
            if show_edit:
                rows.append(
                    [
                        simple_button(f"✏️ {major}", f"major:edit:{major}"),
                        simple_button(f"🗑️ {major}", f"major:delete:{major}"),
                    ]
                )
            else:
                rows.append([simple_button(f"🗑️ {major}", f"major:delete:{major}")])
    rows.append([simple_button("➕ Add Major", "major:add")])
    source = context.user_data.get(STATE_MANAGE_MAJORS)
    back_target = "menu:data" if source == "data" else "menu:students"
    rows.append([simple_button("⬅️ Back", back_target)])
    keyboard = build_menu(rows)
    message = f"Manage majors for {grade}:"
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=keyboard)


async def _start_add_major(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[STATE_ADDING_MAJOR] = True
    source = context.user_data.get(STATE_MANAGE_MAJORS)
    back_target = "menu:data" if source == "data" else "menu:students"
    keyboard = build_menu([[simple_button("⬅️ Cancel", back_target)]])
    await update.callback_query.edit_message_text(
        "Send the new major name.",
        reply_markup=keyboard,
    )


async def _start_edit_major(
    update: Update, context: ContextTypes.DEFAULT_TYPE, major: str
) -> None:
    context.user_data[STATE_EDITING_MAJOR] = major
    source = context.user_data.get(STATE_MANAGE_MAJORS)
    back_target = "menu:data" if source == "data" else "menu:students"
    keyboard = build_menu([[simple_button("⬅️ Cancel", back_target)]])
    await update.callback_query.edit_message_text(
        f"Send the new name for major: {major}",
        reply_markup=keyboard,
    )


async def _handle_major_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    grade = context.user_data.get(STATE_GRADE)
    if not grade:
        await update.message.reply_text("Please select a grade first.")
        return

    major = (update.message.text or "").strip()
    if not major:
        await update.message.reply_text("Please send a valid major name.")
        return

    with session_scope(handler_context.database) as session:
        existing = (
            session.query(Major)
            .filter(Major.grade == grade, Major.name == major)
            .first()
        )
        if existing:
            await update.message.reply_text("That major already exists for this grade.")
            return
        session.add(Major(grade=grade, name=major))

    context.user_data.pop(STATE_ADDING_MAJOR, None)
    await update.message.reply_text(f"Added major: {major}")
    await _show_major_management(update, context)


async def _handle_major_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    grade = context.user_data.get(STATE_GRADE)
    old_major = context.user_data.get(STATE_EDITING_MAJOR)
    if not grade or not old_major:
        await update.message.reply_text("Please select a grade and major first.")
        return

    new_major = (update.message.text or "").strip()
    if not new_major:
        await update.message.reply_text("Please send a valid major name.")
        return

    with session_scope(handler_context.database) as session:
        record = (
            session.query(Major)
            .filter(Major.grade == grade, Major.name == old_major)
            .first()
        )
        if not record:
            await update.message.reply_text("Major not found.")
            return
        existing = (
            session.query(Major)
            .filter(Major.grade == grade, Major.name == new_major)
            .first()
        )
        if existing:
            await update.message.reply_text("That major already exists for this grade.")
            return
        record.name = new_major
        session.query(Student).filter(
            Student.grade == grade, Student.major == old_major
        ).update({Student.major: new_major})

    context.user_data.pop(STATE_EDITING_MAJOR, None)
    await update.message.reply_text(f"Updated major to: {new_major}")
    await _show_major_management(update, context)


async def _handle_teacher_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    text = (update.message.text or "").strip()
    if not text.isdigit():
        await update.message.reply_text("Please send a numeric Telegram user ID.")
        return

    teacher_id = int(text)
    if teacher_id in handler_context.config.authorized_teacher_ids:
        await update.message.reply_text("That teacher ID is already authorized.")
        context.user_data.pop(STATE_ADDING_TEACHER, None)
        await _show_management_menu(update, context)
        return

    with session_scope(handler_context.database) as session:
        existing = session.get(AuthorizedTeacher, teacher_id)
        if existing:
            await update.message.reply_text("That teacher ID is already authorized.")
            context.user_data.pop(STATE_ADDING_TEACHER, None)
            await _show_management_menu(update, context)
            return
        session.add(AuthorizedTeacher(telegram_id=teacher_id))

    context.user_data.pop(STATE_ADDING_TEACHER, None)
    await update.message.reply_text(f"Added teacher ID: {teacher_id}")
    await _show_management_menu(update, context)


async def _show_grade_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    with session_scope(handler_context.database) as session:
        grades = session.query(Grade).order_by(Grade.name.asc()).all()

    rows = []
    if grades:
        for grade in grades:
            rows.append(
                [
                    simple_button(f"✏️ {grade.name}", f"grade:edit:{grade.name}"),
                    simple_button(f"🗑️ {grade.name}", f"grade:delete:{grade.name}"),
                ]
            )
    rows.append([simple_button("➕ Add Grade", "grade:add")])
    rows.append([simple_button("⬅️ Back", "menu:data")])
    keyboard = build_menu(rows)
    message = "Manage grades:"
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=keyboard)


async def _start_add_grade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[STATE_ADDING_GRADE] = True
    keyboard = build_menu([[simple_button("⬅️ Cancel", "menu:data")]])
    await update.callback_query.edit_message_text(
        "Send the new grade name (e.g., 10th).",
        reply_markup=keyboard,
    )


async def _handle_grade_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    grade = (update.message.text or "").strip()
    if not grade:
        await update.message.reply_text("Please send a valid grade name.")
        return

    with session_scope(handler_context.database) as session:
        existing = session.query(Grade).filter(Grade.name == grade).first()
        if existing:
            await update.message.reply_text("That grade already exists.")
            return
        session.add(Grade(name=grade))

    context.user_data.pop(STATE_ADDING_GRADE, None)
    await update.message.reply_text(f"Added grade: {grade}")
    await _show_grade_management(update, context)


async def _start_edit_grade(update: Update, context: ContextTypes.DEFAULT_TYPE, grade: str) -> None:
    context.user_data[STATE_EDITING_GRADE] = grade
    keyboard = build_menu([[simple_button("⬅️ Cancel", "menu:data")]])
    await update.callback_query.edit_message_text(
        f"Send the new name for grade: {grade}",
        reply_markup=keyboard,
    )


async def _handle_grade_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    old_grade = context.user_data.get(STATE_EDITING_GRADE)
    if not old_grade:
        await update.message.reply_text("Please select a grade first.")
        return

    new_grade = (update.message.text or "").strip()
    if not new_grade:
        await update.message.reply_text("Please send a valid grade name.")
        return

    with session_scope(handler_context.database) as session:
        record = session.query(Grade).filter(Grade.name == old_grade).first()
        if not record:
            await update.message.reply_text("Grade not found.")
            return
        existing = session.query(Grade).filter(Grade.name == new_grade).first()
        if existing:
            await update.message.reply_text("That grade already exists.")
            return
        record.name = new_grade
        session.query(Major).filter(Major.grade == old_grade).update({Major.grade: new_grade})
        session.query(Student).filter(Student.grade == old_grade).update({Student.grade: new_grade})

    context.user_data.pop(STATE_EDITING_GRADE, None)
    await update.message.reply_text(f"Updated grade to: {new_grade}")
    await _show_grade_management(update, context)


async def _delete_grade(update: Update, context: ContextTypes.DEFAULT_TYPE, grade: str) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    with session_scope(handler_context.database) as session:
        record = session.query(Grade).filter(Grade.name == grade).first()
        if not record:
            await update.callback_query.edit_message_text("Grade not found.")
            return
        has_students = session.query(Student).filter(Student.grade == grade).first()
        has_majors = session.query(Major).filter(Major.grade == grade).first()
        if has_students or has_majors:
            await update.callback_query.edit_message_text(
                "Cannot delete a grade with students or majors assigned.",
                reply_markup=build_menu([[simple_button("⬅️ Back", "menu:data")]]),
            )
            return
        session.delete(record)

    await _show_grade_management(update, context)


async def _delete_major(update: Update, context: ContextTypes.DEFAULT_TYPE, major: str) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grade = context.user_data.get(STATE_GRADE)
    if not grade:
        await update.callback_query.edit_message_text("Please select a grade first.")
        return

    with session_scope(handler_context.database) as session:
        record = (
            session.query(Major)
            .filter(Major.grade == grade, Major.name == major)
            .first()
        )
        if not record:
            await update.callback_query.edit_message_text("Major not found.")
            return

        student_exists = (
            session.query(Student)
            .filter(Student.grade == grade, Student.major == major)
            .first()
        )
        if student_exists:
            await update.callback_query.edit_message_text(
                "Cannot delete a major with students assigned.",
                reply_markup=build_menu([[simple_button("⬅️ Back", "menu:students")]]),
            )
            return
        session.delete(record)

    await _show_major_management(update, context)


async def _handle_major_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, major: str
) -> None:
    context.user_data[STATE_MAJOR] = major
    context.user_data[STATE_PAGE] = 0

    if context.user_data.get(STATE_ADDING_STUDENTS):
        keyboard = build_menu([[simple_button("⬅️ Cancel", "menu:main")]])
        await update.callback_query.edit_message_text(
            "Send student entries in this format:\n"
            "`STUDENT_ID,Full Name`\n"
            "One student per line. Example:\n"
            "`A1001,Alex Johnson`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )
        return

    if context.user_data.get(STATE_ABSENCE_SELECTION):
        await _show_absence_list(update, context)
        return

    if context.user_data.get(STATE_MANAGE_STUDENTS):
        await _show_student_management_list(update, context)
        return

    await _show_student_list(update, context)


async def _handle_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int) -> None:
    context.user_data[STATE_PAGE] = max(page, 0)

    if context.user_data.get(STATE_ABSENCE_SELECTION):
        await _show_absence_list(update, context)
        return

    if context.user_data.get(STATE_MANAGE_STUDENTS):
        await _show_student_management_list(update, context)
        return

    await _show_student_list(update, context)


async def _handle_student_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    text = (update.message.text or "").strip()
    grade = context.user_data.get(STATE_GRADE)
    major = context.user_data.get(STATE_MAJOR)

    if not grade or not major:
        await update.message.reply_text("Please select a grade and major first.")
        return

    if not text:
        await update.message.reply_text("No data received. Please send student entries.")
        return

    entries = [line.strip() for line in text.splitlines() if line.strip()]
    parsed = []
    errors = []
    for line in entries:
        if "," not in line:
            errors.append(f"Invalid format: {line}")
            continue
        student_id, full_name = [part.strip() for part in line.split(",", 1)]
        if not student_id or not full_name:
            errors.append(f"Missing data: {line}")
            continue
        parsed.append((student_id, full_name))

    if not parsed:
        await update.message.reply_text(
            "No valid entries found. Use `STUDENT_ID,Full Name`.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    added = 0
    skipped = 0
    # Dedupe in-memory to avoid batch duplicates rolling back the transaction.
    seen_ids: set[str] = set()
    seen_name_keys: set[tuple[str, str, str]] = set()
    unique_parsed: list[tuple[str, str]] = []
    for student_id, full_name in parsed:
        name_key = (full_name, grade, major)
        if student_id in seen_ids or name_key in seen_name_keys:
            skipped += 1
            continue
        seen_ids.add(student_id)
        seen_name_keys.add(name_key)
        unique_parsed.append((student_id, full_name))
    with session_scope(handler_context.database) as session:
        for student_id, full_name in unique_parsed:
            existing = session.get(Student, student_id)
            if existing:
                skipped += 1
                continue
            duplicate = (
                session.query(Student)
                .filter(Student.full_name == full_name, Student.grade == grade, Student.major == major)
                .first()
            )
            if duplicate:
                skipped += 1
                continue
            session.add(Student(id=student_id, full_name=full_name, grade=grade, major=major))
            added += 1

    response = [f"Added {added} student(s)."]
    if skipped:
        response.append(f"Skipped {skipped} duplicate(s).")
    if errors:
        response.append("Errors:\n" + "\n".join(errors))

    await update.message.reply_text("\n".join(response))
    context.user_data.clear()
    await _show_main_menu(update, context)


async def _show_student_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grade = context.user_data.get(STATE_GRADE)
    major = context.user_data.get(STATE_MAJOR)
    page = context.user_data.get(STATE_PAGE, 0)

    if not grade or not major:
        message = "Please select grade and major."
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    with session_scope(handler_context.database) as session:
        students = (
            session.query(Student)
            .filter(Student.grade == grade, Student.major == major)
            .order_by(Student.full_name.asc())
            .all()
        )

    if not students:
        await update.callback_query.edit_message_text(
            "No students found for this class.",
            reply_markup=build_menu([[simple_button("⬅️ Back", "menu:students")]]),
        )
        return

    max_page = max((len(students) - 1) // handler_context.config.page_size, 0)
    page = min(page, max_page)
    context.user_data[STATE_PAGE] = page

    items = [InlineKeyboardButton(s.full_name, callback_data="noop") for s in students]
    keyboard = paginated_buttons(
        items,
        page,
        handler_context.config.page_size,
        "menu:students",
    )
    await update.callback_query.edit_message_text(
        f"Students in {grade} - {major}:", reply_markup=keyboard
    )


async def _show_student_management_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grade = context.user_data.get(STATE_GRADE)
    major = context.user_data.get(STATE_MAJOR)
    page = context.user_data.get(STATE_PAGE, 0)

    if not grade or not major:
        await update.callback_query.edit_message_text("Please select grade and major.")
        return

    with session_scope(handler_context.database) as session:
        students = (
            session.query(Student)
            .filter(Student.grade == grade, Student.major == major)
            .order_by(Student.full_name.asc())
            .all()
        )

    if not students:
        message = "No students found for this class."
        keyboard = build_menu([[simple_button("⬅️ Back", "data:students")]])
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text(message, reply_markup=keyboard)
        return

    max_page = max((len(students) - 1) // handler_context.config.page_size, 0)
    page = min(page, max_page)
    context.user_data[STATE_PAGE] = page

    items = [
        InlineKeyboardButton(
            f"{student.full_name}", callback_data=f"student:manage:{student.id}"
        )
        for student in students
    ]
    keyboard = paginated_buttons(
        items,
        page,
        handler_context.config.page_size,
        "data:students",
    )
    message = f"Manage students in {grade} - {major}:"
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=keyboard)


async def _show_student_management_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE, student_id: str
) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    with session_scope(handler_context.database) as session:
        student = session.get(Student, student_id)

    if not student:
        await update.callback_query.edit_message_text("Student not found.")
        return

    keyboard = build_menu(
        [
            [simple_button("✏️ Edit Student", f"student:edit:{student.id}")],
            [simple_button("🗑️ Delete Student", f"student:delete:{student.id}")],
            [simple_button("⬅️ Back", "students:manage")],
        ]
    )
    message = (
        f"Student: {student.full_name}\n"
        f"ID: {student.id}\n"
        f"Grade: {student.grade}\n"
        f"Major: {student.major}"
    )
    await update.callback_query.edit_message_text(message, reply_markup=keyboard)


async def _start_edit_student(
    update: Update, context: ContextTypes.DEFAULT_TYPE, student_id: str
) -> None:
    context.user_data[STATE_EDITING_STUDENT] = student_id
    keyboard = build_menu([[simple_button("⬅️ Cancel", "students:manage")]])
    await update.callback_query.edit_message_text(
        "Send updated student info in this format:\n"
        "`Full Name, Grade, Major`\n"
        "Example:\n"
        "`Alex Johnson, 10th, Science`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )


async def _handle_student_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    student_id = context.user_data.get(STATE_EDITING_STUDENT)
    if not student_id:
        await update.message.reply_text("Please select a student first.")
        return

    text = (update.message.text or "").strip()
    if not text or "," not in text:
        await update.message.reply_text(
            "Please use the format: Full Name, Grade, Major."
        )
        return

    parts = [part.strip() for part in text.split(",", 2)]
    if len(parts) != 3 or not all(parts):
        await update.message.reply_text(
            "Please use the format: Full Name, Grade, Major."
        )
        return

    full_name, grade, major = parts

    with session_scope(handler_context.database) as session:
        student = session.get(Student, student_id)
        if not student:
            await update.message.reply_text("Student not found.")
            return
        grade_record = session.query(Grade).filter(Grade.name == grade).first()
        if not grade_record:
            await update.message.reply_text("That grade does not exist.")
            return
        major_record = (
            session.query(Major)
            .filter(Major.grade == grade, Major.name == major)
            .first()
        )
        if not major_record:
            await update.message.reply_text("That major does not exist for the grade.")
            return
        duplicate = (
            session.query(Student)
            .filter(
                Student.id != student_id,
                Student.full_name == full_name,
                Student.grade == grade,
                Student.major == major,
            )
            .first()
        )
        if duplicate:
            await update.message.reply_text(
                "Another student already exists with that name, grade, and major."
            )
            return
        student.full_name = full_name
        student.grade = grade
        student.major = major

    context.user_data.pop(STATE_EDITING_STUDENT, None)
    await update.message.reply_text("Student updated.")
    await _show_student_management_list(update, context)


async def _delete_student(
    update: Update, context: ContextTypes.DEFAULT_TYPE, student_id: str
) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    with session_scope(handler_context.database) as session:
        student = session.get(Student, student_id)
        if not student:
            await update.callback_query.edit_message_text("Student not found.")
            return
        session.query(Absence).filter(Absence.student_id == student_id).delete()
        session.delete(student)

    await _show_student_management_list(update, context)


async def _show_absence_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    grade = context.user_data.get(STATE_GRADE)
    major = context.user_data.get(STATE_MAJOR)
    page = context.user_data.get(STATE_PAGE, 0)

    if not grade or not major:
        await update.callback_query.edit_message_text("Please select grade and major.")
        return

    with session_scope(handler_context.database) as session:
        students = (
            session.query(Student)
            .filter(Student.grade == grade, Student.major == major)
            .order_by(Student.full_name.asc())
            .all()
        )

    if not students:
        await update.callback_query.edit_message_text(
            "No students found for this class.",
            reply_markup=build_menu([[simple_button("⬅️ Back", "menu:main")]]),
        )
        return

    max_page = max((len(students) - 1) // handler_context.config.page_size, 0)
    page = min(page, max_page)
    context.user_data[STATE_PAGE] = page

    selected = context.user_data.setdefault(STATE_SELECTED_STUDENTS, set())
    buttons: List[InlineKeyboardButton] = []
    for student in students:
        is_selected = student.id in selected
        label = f"{'✅' if is_selected else '⬜️'} {student.full_name}"
        buttons.append(InlineKeyboardButton(label, callback_data=f"absence:toggle:{student.id}"))

    extra_buttons = [
        simple_button("✅ Confirm Absence", "absence:confirm"),
        simple_button("⬅️ Back", "absence:cancel"),
    ]

    keyboard = paginated_buttons(
        buttons,
        page,
        handler_context.config.page_size,
        "menu:main",
        extra_buttons=extra_buttons,
    )
    await update.callback_query.edit_message_text(
        f"Mark absences for {grade} - {major}:", reply_markup=keyboard
    )


async def _toggle_absence_student(
    update: Update, context: ContextTypes.DEFAULT_TYPE, student_id: str
) -> None:
    selected: set = context.user_data.setdefault(STATE_SELECTED_STUDENTS, set())
    if student_id in selected:
        selected.remove(student_id)
    else:
        selected.add(student_id)
    await _show_absence_list(update, context)


async def _confirm_absences(
    update: Update, context: ContextTypes.DEFAULT_TYPE, handler_context: HandlerContext
) -> None:
    selected: set = context.user_data.get(STATE_SELECTED_STUDENTS, set())
    if not selected:
        await update.callback_query.edit_message_text(
            "No students selected.",
            reply_markup=build_menu([[simple_button("⬅️ Back", "menu:main")]]),
        )
        return

    teacher_id = update.effective_user.id
    now = datetime.now(ZoneInfo(handler_context.config.timezone))
    absence_date = now.date()
    created_at = now

    inserted = 0
    skipped = 0

    with session_scope(handler_context.database) as session:
        for student_id in selected:
            exists = (
                session.query(Absence)
                .filter(Absence.student_id == student_id, Absence.absence_date == absence_date)
                .first()
            )
            if exists:
                skipped += 1
                continue
            session.add(
                Absence(
                    student_id=student_id,
                    teacher_id=teacher_id,
                    absence_date=absence_date,
                    created_at=created_at,
                )
            )
            inserted += 1

    message = f"Recorded {inserted} absence(s)."
    if skipped:
        message += f" Skipped {skipped} duplicate(s) for today."

    await update.callback_query.edit_message_text(message)
    context.user_data.clear()
    await _show_main_menu(update, context)


def _resolve_database_path(config: BotConfig) -> Path:
    return Path(config.database.sqlite_path).expanduser().resolve()


def _create_database_backup(config: BotConfig) -> Path:
    source_path = _resolve_database_path(config)
    if not source_path.exists():
        raise FileNotFoundError(f"Database file not found at {source_path}")

    with tempfile.NamedTemporaryFile(prefix="absence_bot_backup_", suffix=".sqlite3", delete=False) as handle:
        backup_path = Path(handle.name)

    with sqlite3.connect(source_path) as source, sqlite3.connect(backup_path) as dest:
        source.backup(dest)

    return backup_path


async def _send_database_backup(
    context: ContextTypes.DEFAULT_TYPE,
    handler_context: HandlerContext,
    user_id: int,
    caption: str,
) -> None:
    try:
        backup_path = _create_database_backup(handler_context.config)
    except FileNotFoundError:
        await context.bot.send_message(
            chat_id=user_id,
            text="Database file not found. Please check the sqlite_path setting.",
        )
        return

    try:
        with backup_path.open("rb") as backup_file:
            await context.bot.send_document(
                chat_id=user_id,
                document=backup_file,
                filename=backup_path.name,
                caption=caption,
            )
    finally:
        backup_path.unlink(missing_ok=True)


async def scheduled_database_export(context: ContextTypes.DEFAULT_TYPE) -> None:
    handler_context: HandlerContext = context.bot_data["handler_context"]
    recipients = handler_context.config.management_user_ids
    if not recipients:
        LOGGER.info("No management users configured for automatic exports.")
        return

    for user_id in recipients:
        await _send_database_backup(
            context,
            handler_context,
            user_id,
            "⏰ Automated database export",
        )


def _is_management(user_id: int, config: BotConfig) -> bool:
    return user_id in config.management_user_ids


def _is_authorized(user_id: int, handler_context: HandlerContext) -> bool:
    config = handler_context.config
    if user_id in config.authorized_teacher_ids or user_id in config.management_user_ids:
        return True
    with session_scope(handler_context.database) as session:
        return session.get(AuthorizedTeacher, user_id) is not None
