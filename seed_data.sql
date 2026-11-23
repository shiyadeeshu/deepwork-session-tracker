-- Sample data for the Deep Work Session Tracker.
-- Apply with:  python seed.py      (or: sqlite3 deepwork.db < seed_data.sql)
-- Re-runnable: wipes existing rows first. All timestamps are UTC.

PRAGMA foreign_keys = ON;
DELETE FROM interruptions;
DELETE FROM sessions;
DELETE FROM sqlite_sequence WHERE name IN ('sessions', 'interruptions');

-- 1. completed: 50 min, paused 2x, finished at 52 min (within the 55-min limit)
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, end_time, status, created_at)
VALUES (1, 'Write report intro', 'Finish first draft of the intro', 50,
        '2026-11-20 09:00:00', '2026-11-20 09:52:00', 'completed', '2026-11-20 08:55:00');
INSERT INTO interruptions (session_id, reason, pause_time) VALUES
  (1, 'Phone call',       '2026-11-20 09:15:00'),
  (1, 'Coffee refill',    '2026-11-20 09:30:00');

-- 2. interrupted: paused 4x
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, end_time, status, created_at)
VALUES (2, 'Refactor auth module', 'Extract token logic', 45,
        '2026-11-20 13:00:00', '2026-11-20 13:35:00', 'interrupted', '2026-11-20 12:50:00');
INSERT INTO interruptions (session_id, reason, pause_time) VALUES
  (2, 'Slack ping',       '2026-11-20 13:05:00'),
  (2, 'Standup',          '2026-11-20 13:12:00'),
  (2, 'Delivery at door', '2026-11-20 13:25:00'),
  (2, 'Manager question', '2026-11-20 13:35:00');

-- 3. abandoned: paused once, never resumed (end_time = pause time)
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, end_time, status, created_at)
VALUES (3, 'Read research paper', 'Summarise section 3', 30,
        '2026-11-21 10:00:00', '2026-11-21 10:12:00', 'abandoned', '2026-11-21 09:58:00');
INSERT INTO interruptions (session_id, reason, pause_time) VALUES
  (3, 'Urgent production bug', '2026-11-21 10:12:00');

-- 4. overdue: 50 min session completed after 60 min (> 55-min limit)
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, end_time, status, created_at)
VALUES (4, 'Prepare slides', 'Q4 review deck', 50,
        '2026-11-21 14:00:00', '2026-11-21 15:00:00', 'overdue', '2026-11-21 13:55:00');
INSERT INTO interruptions (session_id, reason, pause_time) VALUES
  (4, 'Printer jam', '2026-11-21 14:20:00');

-- 5. completed: no pauses
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, end_time, status, created_at)
VALUES (5, 'Code review', 'Review 3 open PRs', 25,
        '2026-11-22 11:00:00', '2026-11-22 11:24:00', 'completed', '2026-11-22 10:59:00');

-- 6. scheduled: not started yet
INSERT INTO sessions (id, title, goal, scheduled_duration, status)
VALUES (6, 'Plan next sprint', 'Draft backlog priorities', 40, 'scheduled');

-- 7. active: started 10 minutes ago (relative to when the seed is applied)
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, status)
VALUES (7, 'Write unit tests', 'Cover pause rules', 60, datetime('now', '-10 minutes'), 'active');

-- 8. paused: started 5 minutes ago, paused 1 minute ago
INSERT INTO sessions (id, title, goal, scheduled_duration, start_time, status)
VALUES (8, 'Learn Alembic', 'Understand batch migrations', 90, datetime('now', '-5 minutes'), 'paused');
INSERT INTO interruptions (session_id, reason, pause_time) VALUES
  (8, 'Lunch', datetime('now', '-1 minutes'));
