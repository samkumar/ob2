import logging

import ob2.config as config
from ob2.database import DbCursor
from ob2.util.build_constants import QUEUED, IN_PROGRESS, FAILED
from ob2.util.time import now_str

try:
    MAX_JOBS_ALLOWED = config.max_ongoing_jobs
    assert isinstance(MAX_JOBS_ALLOWED, int)
except (AttributeError, AssertionError):
    MAX_JOBS_ALLOWED = None

def rate_limit_fail_build(build_name):
    assert MAX_JOBS_ALLOWED is not None
    message = "Cannot have more than {} builds in progress or queued.".format(MAX_JOBS_ALLOWED)
    with DbCursor() as c:
        c.execute('''UPDATE builds SET status = ?, updated = ?, log = ?
                     WHERE build_name = ?''', [FAILED, now_str(), message, build_name])

def should_limit_source(repo_name):
    if MAX_JOBS_ALLOWED is None:
        return False
    with DbCursor() as c:
        c.execute('''SELECT count(*) FROM builds
                                WHERE source = ? AND (status = ? OR status = ?)''',
                  [repo_name, QUEUED, IN_PROGRESS])
        count = int(c.fetchone()[0])
        return count > MAX_JOBS_ALLOWED
