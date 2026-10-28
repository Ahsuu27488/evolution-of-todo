"""Email templates and the unsubscribe status page: escaping, palette, copy (no DB needed)."""

import re

import pytest

from app.routes.notifications import _status_page
from app.services.email_service import EmailTemplates, friendly_due

LEGACY = ["#00f5ff", "#a855f7", "#0891b2", "linear-gradient", "Chronos Todo"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def all_templates(title: str = "Pay rent") -> dict[str, str]:
    return {
        "due": EmailTemplates.task_due(title, "Thu 29 Oct, 17:00", "/dashboard?task=1", "tok"),
        "overdue": EmailTemplates.task_overdue(title, "Tue 27 Oct, 10:00", "/dashboard?task=1", "tok"),
        "assigned": EmailTemplates.task_assigned(title, "Kairos", "/dashboard?task=1", "tok"),
        "digest": EmailTemplates.daily_digest([{"title": title, "due_date": "Today 17:00"}]),
        "weekly": EmailTemplates.weekly_summary({"completed": 3, "pending": 2, "overdue": 1}),
        "welcome": EmailTemplates.welcome("ayla@example.test", "Ayla", "tok"),
        "message": EmailTemplates.message("Test email", "It works", "tok"),
    }


@pytest.mark.parametrize("name", list(all_templates()))
def test_templates_use_the_new_palette_without_emoji(name):
    html = all_templates()[name]
    for legacy in LEGACY:
        assert legacy not in html, f"{name} still contains {legacy}"
    assert not EMOJI.search(html), f"{name} contains an emoji"
    assert "prefers-color-scheme: dark" in html
    assert "#F2B84B" in html  # sun gold button


def test_task_titles_are_html_escaped():
    evil = '<img src=x onerror="alert(1)">'
    for name, html in all_templates(evil).items():
        if name in ("weekly", "welcome", "message"):
            continue
        assert evil not in html, name
        assert "&lt;img src=x" in html, name


def test_unsubscribe_link_only_with_token():
    assert "Unsubscribe" in EmailTemplates.task_due("a", "b", "/d", "tok")
    assert "Unsubscribe" not in EmailTemplates.daily_digest([])


def test_friendly_due_formats_iso_and_keeps_fallbacks():
    assert friendly_due("2026-10-29T17:00:00") == "Thu 29 Oct, 17:00"
    assert friendly_due(None) == "No due date"
    assert friendly_due("tomorrow") == "tomorrow"


def test_status_page_escapes_and_themes():
    page = _status_page("http://x", "Done <b>", "msg & more", ok=True)
    assert "Done &lt;b&gt;" in page
    assert "msg &amp; more" in page
    assert "prefers-color-scheme: dark" in page
    assert "linear-gradient" not in page
