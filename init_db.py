import os
import sys
from werkzeug.security import generate_password_hash

# Ensure we import the app package after adjusting cwd
cwd = os.getcwd()
# Try both project root and Flask instance folder where the DB may live
db_candidates = [os.path.join(cwd, 'medical_store.db'), os.path.join(cwd, 'instance', 'medical_store.db')]
for db_path in db_candidates:
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f'Removed existing database: {db_path}')
        except Exception as e:
            print(f'Failed to remove existing DB {db_path}: {e}')

# Import app and models
import app as app_module
from app import db, User, Supplier

with app_module.app.app_context():
    db.create_all()
    # Seed admin
    admin = User.query.filter_by(username='Piyu').first()
    hashed = generate_password_hash('Piyu24', method='pbkdf2:sha256')
    if not admin:
        admin = User(username='Piyu', password_hash=hashed, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')
    else:
        admin.password_hash = hashed
        db.session.commit()
        print('Admin updated')

    # Seed supplier
    if not Supplier.query.first():
        supplier = Supplier(
            name='Sample Supplier',
            contact='John Doe',
            email='supplier@example.com',
            phone='+1234567890',
            address='123 Supplier St, City, Country',
            gst_number='22AAAAA0000A1Z5'
        )
        db.session.add(supplier)
        db.session.commit()
        print('Sample supplier created')

print('Database initialization complete')
