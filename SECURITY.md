# Security Notes

## Production requirements

- Set a strong random `SECRET_KEY` through environment variables.
- Never commit `.env`, local databases, credentials, API keys, or generated uploads.
- Use PostgreSQL (or another managed relational database) for production instead of SQLite.
- Run behind HTTPS and a production WSGI server such as Gunicorn.
- Restrict destructive operations to authorized staff/admin users.
- Validate medicine quantities, prices, dates, discounts, and supplier references server-side.
- Keep audit logs for inventory, purchase, sale, and user changes.
- Back up the production database regularly.

## Reporting a vulnerability

Do not publish credentials or exploit details in a public issue. Contact the repository owner privately with reproduction steps and the affected component.
