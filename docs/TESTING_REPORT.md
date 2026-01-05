# AbsenceBot Testing Report

## Summary
The following scenarios were tested to validate correctness, security, and stability.

## Test Scenarios

### 1. Unauthorized Access
- **Steps:** Open bot with an unlisted Telegram user ID.
- **Expected:** Bot returns an unauthorized message and no menu.
- **Actual:** Unauthorized message displayed.
- **Fixes:** None required.

### 2. Empty Student List
- **Steps:** Select a grade/major with no students.
- **Expected:** Friendly message indicating no students.
- **Actual:** Correct message shown.
- **Fixes:** None required.

### 3. Add Students With Invalid Format
- **Steps:** Send malformed lines (missing comma, blank ID).
- **Expected:** Errors listed, no bad records added.
- **Actual:** Invalid entries rejected.
- **Fixes:** Added strict validation in student input handler.

### 4. Duplicate Student Records
- **Steps:** Add the same student ID or name twice.
- **Expected:** Duplicates skipped.
- **Actual:** Skipped with confirmation.
- **Fixes:** Added unique checks and skip counts.

### 5. Absence Duplication
- **Steps:** Mark the same student absent twice on the same day.
- **Expected:** Only one absence stored.
- **Actual:** Duplicate skipped.
- **Fixes:** Added database and application-level checks.

### 6. Large Student Lists
- **Steps:** Add 50+ students and open list.
- **Expected:** Pagination works; no Telegram errors.
- **Actual:** Pagination displayed with next/prev.
- **Fixes:** Implemented pagination helper.

### 7. Callback Edge Cases
- **Steps:** Trigger stale callbacks after state reset.
- **Expected:** Bot responds with invalid action and returns to menu.
- **Actual:** Generic error or invalid action message shown.
- **Fixes:** Added safe default handling.

### 8. Simultaneous Teachers
- **Steps:** Use bot from two authorized accounts in parallel.
- **Expected:** Each teacher has independent state.
- **Actual:** Independent `user_data` per user.
- **Fixes:** None required.
