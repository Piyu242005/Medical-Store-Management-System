# Production Upgrade Plan

This branch hardens the Medical Store Management System for deployment and establishes the next architecture steps.

## Completed

- Added `.gitignore` for Python caches, local databases, secrets, IDE files, and generated uploads.
- Added `.env.example` for environment-based configuration.
- Added a hardened WSGI entrypoint with secure session-cookie settings.
- Added Gunicorn for production serving.
- Added PostgreSQL driver support for production database migration.
- Added security guidance.

## Recommended production architecture

```text
Browser
  -> Flask application / Gunicorn
  -> PostgreSQL
  -> object storage for uploads
```

## Business logic upgrades to implement next

1. Role-based permissions: Admin, Pharmacist, Cashier.
2. Batch-level inventory instead of a single quantity on Medicine.
3. Stock movement ledger for every purchase, sale, return, and adjustment.
4. Expiry alerts for expired and soon-to-expire batches.
5. POS checkout with atomic stock deduction and invoice generation.
6. Profit and margin reporting using purchase cost vs selling price.
7. Audit logs for sensitive operations.
8. Barcode/QR lookup.
9. Database backups and restore workflow.
10. Automated tests for authentication, stock, purchases, sales, and permissions.

## Deployment

Set a strong `SECRET_KEY` and a production `DATABASE_URL` in the hosting platform. Do not commit either value to Git.
