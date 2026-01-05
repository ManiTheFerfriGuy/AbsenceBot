# AbsenceBot Technical Blueprint

## 1. Product Design Requirements (PDR)

**Summary:** AbsenceBot is a secure Telegram bot that lets authorized teachers record and manage student absences quickly with inline keyboards only, optimized for cPanel hosting.

**Vision & Problem Solved**
- **Problem:** Schools need a fast, consistent way to record absences without paper forms or messy spreadsheets.
- **Solution:** A Telegram bot with role-restricted access and a guided, keyboard-only flow for student management and attendance logging.

**Target Users**
- **Primary:** Authorized teachers.
- **Secondary:** School administrators who manage configuration and reports.

**Core Features**
- Teacher authentication via environment variables.
- Student roster management by grade and major.
- Absence recording with duplicate prevention for the same day.
- Error-safe, inline keyboard navigation.

**Functional Requirements**
- Allow only configured teacher IDs.
- Add students in a strict, validated format.
- Prevent duplicate students and duplicate absences (same student, same day).
- Store absences with teacher ID and timestamp.
- Full inline keyboard navigation.

**Non-Functional Requirements**
- High reliability and stable error handling.
- Simple installation on cPanel.
- Clear logging and predictable configuration.
- Maintainability with modular code.

---

## 2. Tech Stack

**Summary:** Python + `python-telegram-bot` with SQLAlchemy and SQLite for cPanel compatibility.

**Backend**
- **Python 3.9+**: Widely supported on cPanel.
- **python-telegram-bot**: Stable, maintained Telegram bot framework.
- **SQLAlchemy**: ORM to reduce raw SQL and support multiple databases (Security Checklist #8).

**Database**
- **SQLite**: Simple local development and production storage with zero external setup.

**Why This Stack**
- Minimal dependencies, easy deployment, and strong community support.
- Aligns with cPanel hosting constraints.

**Security Checklist Integration**
- **Auth library**: Telegram authentication via user IDs; no custom auth system.
- **Protected endpoints**: Every update is checked for authorized user ID.
- **No secrets in frontend**: Bot token and DB creds stored in environment variables only.
- **Secrets in `.gitignore`**: keep environment variables out of version control.
- **Sanitized errors**: Generic error responses to users.
- **RBAC**: Teacher-only access enforced (role-based via ID list).
- **HTTPS**: Webhook deployments should enforce HTTPS.

---

## 3. App Flowchart

**Summary:** Inline keyboard flow ensures each step is guided and validated.

```text
Teacher → /start
  ↓ (Auth check)
Main Menu
  ├─ Manage Students
  │   ├─ Select Grade → Select Major → Add Students (validated format)
  │   └─ Select Grade → Select Major → View Students (paginated list)
  └─ Record Absence
      ├─ Select Grade → Select Major
      ├─ Select Students (multi-select)
      └─ Confirm → Store Absence (dedupe per day)

Data Flow:
Telegram Update → Bot Handler → Validation → Database (SQLite)
```

---

## 4. Project Rules

**Summary:** Keep the project stable, secure, and maintainable.

- **Coding Standards**: PEP 8, clear naming, docstrings for modules.
- **Version Control**: Feature branches → PR review → main.
- **Testing**: Cover authorization checks, empty class lists, duplicate prevention.
- **Documentation**: Update installation, configuration, and usage docs per change.
- **Performance**: Paginate lists, avoid huge inline keyboards.
- **Accessibility**: Clear text labels, predictable navigation.

---

## 5. Implementation Plan

**Summary:** Incremental milestones with clear dependencies.

1. **Setup & Foundation (Day 1)**
   - Create repo structure, environment configuration, logging, and base bot runner.
2. **Database Layer (Day 2)**
   - Define models and schema.
   - Implement ORM and migrations (optional).
3. **Core Features (Day 3–4)**
   - Teacher authentication
   - Student add/list flows
   - Absence recording flow
4. **Validation & Error Handling (Day 4)**
   - Handle empty lists, invalid callbacks, DB errors.
5. **Testing (Day 5)**
   - Manual test scenarios and documentation.
6. **Deployment Docs (Day 6)**
   - cPanel setup, webhook/long polling guidance.

---

## 6. Frontend Guidelines

**Summary:** Telegram UI is the only interface; keep it clean and simple.

- **Design Principles**: Minimal steps, consistent navigation, clear labels.
- **Component Patterns**: Reusable keyboard builders and pagination.
- **Performance**: Paginate large lists; avoid heavy text payloads.
- **Accessibility**: Use emojis sparingly with labels.

---

## 7. Backend Guidelines

**Summary:** Keep handlers modular, secure, and resilient.

- **Architecture**: Handler-based routing with shared `HandlerContext`.
- **API Design**: Telegram update handlers act like endpoints.
- **Data Storage**: SQLAlchemy models with unique constraints.
- **Security**:
  - **RBAC**: Teacher ID list in environment variables.
  - **Protected handlers**: Every handler checks authorization.
  - **No secrets in code**: Tokens and DB creds in environment variables.
  - **Sanitized errors**: No stack traces to users.
- **Performance**:
  - Pagination and indexed queries.
  - Connection pooling via SQLAlchemy.

---

## 8. Optimised React Code Guidelines

**Summary:** Not used directly in this Telegram bot, but provided for future web dashboards.

### Common Pitfalls
```tsx
// Problem: Inline object causes rerender
<MyComponent style={{ marginTop: 8 }} />
```

### Optimized Approach
```tsx
const style = useMemo(() => ({ marginTop: 8 }), []);
<MyComponent style={style} />
```

### Additional Recommendations
- Use `React.memo` for pure components.
- Wrap callbacks in `useCallback`.
- Split large components into smaller, testable units.
- Avoid heavy computations inside render; memoize results.

---

## 9. Security Checklist (Enforced Across the Stack)

1. **Use a battle-tested auth library** – Telegram auth via user IDs; no custom auth logic.
2. **Lock down protected endpoints** – every update checked against authorized IDs.
3. **Never expose secrets on the frontend** – token/DB creds only in server environment variables.
4. **Git-ignore sensitive files** – avoid committing any local env files or secrets.
5. **Sanitise error messages** – user-facing errors are generic.
6. **Use middleware auth checks** – centralized authorization check in handlers.
7. **Add role-based access control (RBAC)** – teacher role enforced by ID list.
8. **Use secure DB libraries or platforms** – SQLAlchemy ORM prevents raw SQL.
9. **Host on a secure platform** – cPanel with SSL, or cloud providers with WAF/DDoS.
10. **Enable HTTPS everywhere** – required for webhook deployments.
11. **Limit file-upload risks** – no file uploads supported.
