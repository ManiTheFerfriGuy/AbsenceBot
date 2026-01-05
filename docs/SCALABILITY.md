# Future Scalability Notes

## Summary
AbsenceBot is designed for small to mid-sized schools. The following steps can scale it further.

## Recommendations
- **Database Indexing**: Add indexes on `students.grade`, `students.major`, and `absences.absence_date`.
- **Caching**: Cache roster lists for heavy usage periods.
- **Webhook Mode**: Use HTTPS webhooks for reduced polling overhead.
- **Admin Portal**: Build a small web dashboard for reports and exports.
- **Role Expansion**: Add `admin` roles for configuration changes via a secure UI.
