import argparse
import datetime
import logging
import re

import holidays

from github import Github
from github.Issue import Issue

from typing import Iterator

PA_HOLIDAYS = holidays.country_holidays("US", subdiv="PA")

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


def close_old_issues(issues: list[Issue], lifespan: int):
    """
    Closes scrum issues older than the number of days specified by lifespan.
    """
    lifespan = datetime.timedelta(days=lifespan)
    today = get_today()

    for issue in issues:
        date = issue_title_to_date(issue.title)
        if not date:
            continue

        if today - date > lifespan:
            log.info(f"Closing {issue.title}")
            try:
                issue.edit(state="closed")
            except Exception as e:
                log.error("Closing issue failed:", exc_info=True)


def create_scrum_issue(repository, date):
    """
    Creates a scrum issue for the given date.
    """
    body = "\n".join(
        (
            "Please be sure to include:",
            "  - What you worked on yesterday.",
            "  - What you plan on working on today.",
            "  - Any blockers.",
        )
    )
    title = f"{date}: e-scrum for {date:%A, %B %-d, %Y}"

    log.info(f"Creating {title}")
    try:
        repository.create_issue(title=title, body=body)
    except Exception as e:
        log.error("Creating issue failed:", exc_info=True)


def get_future_dates_without_issues(
    issues: list[Issue], workdays_ahead=2
) -> list[datetime.date]:
    """
    Looks through issues and yields the dates of future workdays (includes today)
    that don't have open issues.
    """
    future_dates = set(get_upcoming_workdays(workdays_ahead))
    future_dates -= {issue_title_to_date(issue.title) for issue in issues}

    return sorted(future_dates)


def get_holidays() -> set[str]:
    with open("holidays.txt", "r") as holidays_file:
        lines = [l.strip() for l in holidays_file.readlines()]
    return set([l for l in lines if l and not l.startswith("#")])


def get_today() -> datetime.date:
    """
    Returns the datetime.date for today. Needed since tests cannot mock a
    builtin type: http://stackoverflow.com/a/24005764/4651668
    """
    return datetime.date.today()


def get_upcoming_workdays(workdays_ahead=2) -> Iterator[datetime.date]:
    """
    Returns a generator of the next number of workdays specified by
    workdays_ahead. The current day is yielded first, if a workday,
    and does not count as one of workdays_ahead.
    """
    date = get_today()
    if is_workday(date):
        yield date

    i = 0
    while i < workdays_ahead:
        date += datetime.timedelta(days=1)
        if is_workday(date):
            yield date
            i += 1


def is_holiday(date: datetime.date) -> bool:
    """
    Returns `True` if a date is a holiday.  Returns `False` otherwise.
    """
    return PA_HOLIDAYS.get(date, "").replace(" (Observed)", "") in get_holidays()


def is_workday(date: datetime.date) -> bool:
    """
    Returns `True` if a date is a workday. Returns `False` otherwise.
    """
    return date.weekday() not in holidays.WEEKEND and not is_holiday(date)


def issue_title_to_date(title: str) -> datetime.date:
    """
    Returns a datetime.date object from a scrum issue title.
    """
    pattern = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2}):")
    match = pattern.match(title)
    if match:
        return datetime.date(*map(int, match.groups()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lifespan", type=int, default=7)
    parser.add_argument("--repository", default="AlexsLemonade/scrumlord-test")
    parser.add_argument("--token", help="GitHub access token")
    parser.add_argument("--workdays-ahead", type=int, default=2)
    args = parser.parse_args()

    github = Github(args.token)
    repository = github.get_repo(args.repository)
    issues = repository.get_issues(state="open")

    # Close old issues.
    close_old_issues(issues, args.lifespan)

    # Create upcoming issues.
    for date in get_future_dates_without_issues(issues, args.workdays_ahead):
        create_scrum_issue(repository, date)
