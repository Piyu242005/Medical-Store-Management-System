from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func, extract
import os
import csv
from io import StringIO
import base64

# Optional Pillow imports: try to import for image generation, otherwise fall back.
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = ImageDraw = ImageFont = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    medicines = db.relationship('Medicine', backref='supplier_ref', lazy=True)
    purchases = db.relationship('Purchase', backref='supplier', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default='Pending')
    items = db.relationship('PurchaseItem', backref='purchase', lazy=True, cascade='all, delete-orphan')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_contact = db.Column(db.String(20))
    total_amount = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20), default='Cash')
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SaleItem', backref='sale_ref', lazy=True, cascade='all, delete-orphan')

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    batch_number = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    # Relationship for easy access in templates
    medicine = db.relationship('Medicine', foreign_keys=[medicine_id], lazy='joined')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    batch_number = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    # Relationship for easy access in templates
    medicine = db.relationship('Medicine', foreign_keys=[medicine_id], lazy='joined')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total_medicines = Medicine.query.count()
    total_sales = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
    low_stock_medicines = Medicine.query.filter(Medicine.quantity < 10).count()
    
    return render_template('dashboard.html', 
                         total_medicines=total_medicines,
                         total_sales=total_sales,
                         low_stock_medicines=low_stock_medicines)

@app.route('/medicines')
@login_required
def medicines():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Medicine.query
    
    if search:
        query = query.filter(
            (Medicine.name.ilike(f'%{search}%')) |
            (Medicine.description.ilike(f'%{search}%')) |
            (Medicine.id == search)
        )
    
    medicines_pagination = query.order_by(Medicine.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('medicines.html', medicines=medicines_pagination, search=search)

@app.route('/add_medicine', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = int(request.form.get('quantity', 0))
        price = float(request.form.get('price', 0))
        supplier_id = request.form.get('supplier_id')
        expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        batch_number = request.form.get('batch_number', '')
        
        medicine = Medicine(
            name=name,
            description=description,
            quantity=0,  # Start with 0, will be updated by purchase
            price=price,
            supplier_id=supplier_id if supplier_id else None,
            expiry_date=expiry_date,
            batch_number=batch_number
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        # Create a purchase entry for the initial stock
        if quantity > 0:
            purchase = Purchase(
                supplier_id=supplier_id,
                invoice_number=f'INIT-{medicine.id}-{datetime.utcnow().strftime("%Y%m%d")}',
                total_amount=quantity * price,
                purchase_date=datetime.utcnow().date(),
                payment_status='Paid'
            )
            db.session.add(purchase)
            db.session.flush()  # To get the purchase ID
            
            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                medicine_id=medicine.id,
                batch_number=batch_number,
                quantity=quantity,
                unit_price=price,
                expiry_date=expiry_date
            )
            db.session.add(purchase_item)
            
            # Update medicine quantity
            medicine.quantity += quantity
            db.session.commit()
        
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('medicines'))
    
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('add_medicine.html', suppliers=suppliers)

@app.route('/medicine/<int:id>')
@login_required
def view_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    return render_template('view_medicine.html', medicine=medicine)

@app.route('/medicine/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        medicine.name = request.form.get('name')
        medicine.description = request.form.get('description')
        medicine.price = float(request.form.get('price', 0))
        medicine.supplier_id = request.form.get('supplier_id') or None
        medicine.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        medicine.batch_number = request.form.get('batch_number', '')
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('view_medicine', id=medicine.id))
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('edit_medicine.html', medicine=medicine, suppliers=suppliers)

@app.route('/medicine/<int:id>/delete', methods=['POST'])
@login_required
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines'))

# Suppliers Routes
@app.route('/suppliers')
@login_required
def suppliers():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    query = Supplier.query
    
    if search:
        query = query.filter(
            (Supplier.name.ilike(f'%{search}%')) |
            (Supplier.contact.ilike(f'%{search}%')) |
            (Supplier.email.ilike(f'%{search}%'))
        )
    
    suppliers_pagination = query.order_by(Supplier.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('suppliers.html', suppliers=suppliers_pagination, search=search)

@app.route('/supplier/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        gst_number = request.form.get('gst_number')
        
        supplier = Supplier(
            name=name,
            contact=contact,
            email=email,
            phone=phone,
            address=address,
            gst_number=gst_number
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('add_supplier.html')

@app.route('/supplier/<int:id>')
@login_required
def view_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    medicines = Medicine.query.filter_by(supplier_id=id).all()
    purchases = Purchase.query.filter_by(supplier_id=id).order_by(Purchase.purchase_date.desc()).limit(5).all()
    return render_template('view_supplier.html', supplier=supplier, medicines=medicines, purchases=purchases)

@app.route('/supplier/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact = request.form.get('contact')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.gst_number = request.form.get('gst_number')
        
        db.session.commit()
        
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('view_supplier', id=supplier.id))
    
    return render_template('add_supplier.html', supplier=supplier, edit=True)

@app.route('/supplier/<int:id>/delete', methods=['POST'])
@login_required
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    # Check if supplier has associated medicines
    associated_medicines = Medicine.query.filter_by(supplier_id=id).count()
    if associated_medicines > 0:
        return jsonify({'success': False, 'message': 'Cannot delete supplier with associated medicines. Please reassign or delete the medicines first.'})
    
    try:
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Supplier deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error deleting supplier: ' + str(e)})

# Sales Routes
@app.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    customer = request.args.get('customer', '')
    
    query = Sale.query
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Sale.sale_date >= start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include the entire end date
        query = query.filter(Sale.sale_date <= end_date)
    
    if customer:
        query = query.filter(Sale.customer_name.ilike(f'%{customer}%'))
    
    sales_pagination = query.order_by(Sale.sale_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('sales.html', 
                         sales=sales_pagination,
                         start_date=start_date.strftime('%Y-%m-%d') if start_date else '',
                         end_date=end_date.strftime('%Y-%m-%d') if end_date else '',
                         customer=customer)

@app.route('/sale/new', methods=['GET', 'POST'])
@login_required
def new_sale():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_contact = request.form.get('customer_contact')
        payment_method = request.form.get('payment_method', 'Cash')
        discount = float(request.form.get('discount', 0))
        tax_percentage = float(request.form.get('tax_percentage', 0))
        
        # Generate invoice number
        invoice_number = f'INV-{datetime.utcnow().strftime("%Y%m%d")}-{Sale.query.count() + 1:04d}'
        
        # Calculate total amount from items
        total_amount = 0
        items = []
        
        # Get the items from the form
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for i in range(len(medicine_ids)):
            medicine_id = int(medicine_ids[i])
            quantity = int(quantities[i])
            price = float(prices[i])
            
            if quantity <= 0:
                continue
                
            # Check if enough stock is available
            medicine = Medicine.query.get(medicine_id)
            if not medicine or medicine.quantity < quantity:
                flash(f'Not enough stock for {medicine.name if medicine else "selected medicine"}', 'danger')
                return redirect(url_for('new_sale'))
            
            item_total = quantity * price
            total_amount += item_total
            
            items.append({
                'medicine_id': medicine_id,
                'quantity': quantity,
                'unit_price': price,
                'total_price': item_total,
                'batch_number': medicine.batch_number
            })
        
        # Apply discount
        discount_amount = (total_amount * discount) / 100
        subtotal = total_amount - discount_amount
        
        # Calculate tax
        tax_amount = (subtotal * tax_percentage) / 100
        
        # Calculate final total
        final_total = subtotal + tax_amount
        
        # Create sale record
        sale = Sale(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_contact=customer_contact,
            total_amount=final_total,
            discount=discount_amount,
            tax_amount=tax_amount,
            payment_method=payment_method
        )
        
        db.session.add(sale)
        db.session.flush()  # To get the sale ID
        
        # Add sale items and update stock
        for item in items:
            sale_item = SaleItem(
                sale_id=sale.id,
                medicine_id=item['medicine_id'],
                batch_number=item['batch_number'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price']
            )
            db.session.add(sale_item)
            
            # Update medicine stock
            medicine = Medicine.query.get(item['medicine_id'])
            medicine.quantity -= item['quantity']
        
        db.session.commit()
        
        flash('Sale completed successfully!', 'success')
        return redirect(url_for('view_sale', id=sale.id))
    
    # For GET request, show the sale form
    medicines = Medicine.query.filter(Medicine.quantity > 0).order_by(Medicine.name).all()
    return render_template('new_sale.html', medicines=medicines)

@app.route('/sale/<int:id>')
@login_required
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('view_sale.html', sale=sale)

# Reports Routes
@app.route('/reports')
@login_required
def reports():
    # Get date range for the current month
    today = datetime.utcnow()
    first_day = today.replace(day=1)
    
    # Generate dates for the current month
    dates = [(first_day + timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range((today - first_day).days + 1)]
    
    # Get sales data for the current month
    sales_data = db.session.query(
        func.date(Sale.sale_date).label('sale_date'),
        func.sum(Sale.total_amount).label('total_amount'),
        func.count(Sale.id).label('sale_count')
    ).filter(
        Sale.sale_date >= first_day,
        Sale.sale_date <= today
    ).group_by(
        func.date(Sale.sale_date)
    ).all()
    
    # Create a dictionary of date to sales data
    sales_dict = {str(date): {'amount': 0, 'count': 0} for date in dates}
    for sale in sales_data:
        # sale.sale_date is a string (from func.date()), not a datetime object
        date_str = str(sale.sale_date) if not isinstance(sale.sale_date, str) else sale.sale_date
        if date_str in sales_dict:
            sales_dict[date_str] = {
                'amount': float(sale.total_amount or 0),
                'count': sale.sale_count or 0
            }
    
    # Prepare chart data
    amounts = [sales_dict[date]['amount'] for date in dates]
    counts = [sales_dict[date]['count'] for date in dates]
    
    # Get top selling medicines
    top_medicines = db.session.query(
        Medicine.name,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.total_price).label('total_sales')
    ).join(
        SaleItem, SaleItem.medicine_id == Medicine.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.sale_date >= first_day,
        Sale.sale_date <= today
    ).group_by(
        Medicine.id, Medicine.name
    ).order_by(
        func.sum(SaleItem.quantity).desc()
    ).limit(10).all()
    
    # Get low stock medicines
    low_stock = Medicine.query.filter(Medicine.quantity < 10).all()
    
    # Get payment methods summary
    payment_methods = db.session.query(
        Sale.payment_method,
        func.count(Sale.id).label('sale_count'),
        func.sum(Sale.total_amount).label('total_amount')
    ).filter(
        Sale.sale_date >= first_day,
        Sale.sale_date <= today
    ).group_by(
        Sale.payment_method
    ).all()
    
    return render_template('reports.html',
                         start_date=first_day,
                         end_date=today,
                         dates=dates,
                         amounts=amounts,
                         counts=counts,
                         top_medicines=top_medicines,
                         low_stock=low_stock,
                         payment_methods=payment_methods)

# Export reports as CSV
@app.route('/export/report/<string:report_type>')
@login_required
def export_report(report_type):
    if report_type == 'sales':
        # Get sales data
        sales = db.session.query(
            Sale.invoice_number,
            Sale.sale_date,
            Sale.customer_name,
            Sale.total_amount,
            Sale.payment_method
        ).order_by(Sale.sale_date.desc()).all()
        
        # Create CSV data
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Invoice #', 'Date', 'Customer', 'Total Amount', 'Payment Method'])
        
        for sale in sales:
            cw.writerow([
                sale.invoice_number,
                sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                sale.customer_name,
                f"{sale.total_amount:.2f}",
                sale.payment_method
            ])
        
        # Prepare the response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=sales_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    
    elif report_type == 'inventory':
        # Get inventory data
        inventory = db.session.query(
            Medicine.name,
            Medicine.batch_number,
            Medicine.quantity,
            Medicine.price,
            Supplier.name.label('supplier_name')
        ).outerjoin(
            Supplier, Medicine.supplier_id == Supplier.id
        ).order_by(
            Medicine.quantity.asc()
        ).all()
        
        # Create CSV data
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['Medicine', 'Batch Number', 'Quantity', 'Price (₹)', 'Supplier'])
        
        for item in inventory:
            cw.writerow([
                item.name,
                item.batch_number or 'N/A',
                item.quantity,
                f"{float(item.price):.2f}",
                item.supplier_name or 'N/A'
            ])
        
        # Prepare the response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=inventory_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    
    flash('Invalid report type', 'error')
    return redirect(url_for('reports'))

@app.route('/reports/export')
@login_required
def export_reports():
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report_type = request.args.get('type', 'sales')
    
    # Convert string dates to datetime objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Create a file-like buffer to receive CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    if report_type == 'sales':
        # Sales Report
        query = Sale.query
        
        if start_date and end_date:
            query = query.filter(Sale.sale_date.between(start_date, end_date))
        
        sales = query.order_by(Sale.sale_date.desc()).all()
        
        # Write CSV header
        cw.writerow(['Invoice #', 'Date', 'Customer', 'Items', 'Subtotal', 'Discount', 'Tax', 'Total', 'Payment Method'])
        
        # Write data rows
        for sale in sales:
            item_count = sum(item.quantity for item in sale.items)
            cw.writerow([
                sale.invoice_number,
                sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                sale.customer_name,
                item_count,
                sale.total_amount - sale.tax_amount + sale.discount,
                sale.discount,
                sale.tax_amount,
                sale.total_amount,
                sale.payment_method
            ])
        
        filename = f'sales_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    
    elif report_type == 'inventory':
        # Inventory Report
        medicines = Medicine.query.order_by(Medicine.name).all()
        
        # Write CSV header
        cw.writerow(['ID', 'Name', 'Description', 'Batch #', 'Quantity', 'Price', 'Supplier', 'Expiry Date'])
        
        # Write data rows
        for med in medicines:
            cw.writerow([
                med.id,
                med.name,
                med.description or '',
                med.batch_number or '',
                med.quantity,
                med.price,
                med.supplier_ref.name if med.supplier_ref else '',
                med.expiry_date.strftime('%Y-%m-%d') if med.expiry_date else ''
            ])
        
        filename = f'inventory_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    
    # Prepare the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    
    return output

# Static files for logo
@app.route('/static/logo.png')
def serve_logo():
    # If logo.png doesn't exist, create a default one
    logo_path = os.path.join('static', 'logo.png')
    if not os.path.exists(logo_path):
        # Try to create a simple raster image using Pillow if available.
        # If Pillow is not installed, fall back to a simple SVG placeholder so
        # the app doesn't crash due to an ImportError.
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io

            # Create a blank image with a light blue background
            img = Image.new('RGB', (200, 100), color='#e9f5ff')
            d = ImageDraw.Draw(img)

            # Try to use a default font, fallback to basic font if not available
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()

            # Draw text
            d.text((10, 10), "Medical", fill=(0, 0, 0), font=font)
            d.text((10, 40), "Store", fill=(0, 0, 0), font=font)

            # Save the image to a bytes buffer
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)

            # Save the image to disk for future use
            img.save(logo_path)

            # Return the image
            return send_file(img_io, mimetype='image/png')
        except ImportError:
            # Pillow not installed — return a small SVG placeholder instead
            svg = """
            <svg xmlns='http://www.w3.org/2000/svg' width='200' height='100'>
              <rect width='100%' height='100%' fill='#e9f5ff'/>
              <text x='10' y='30' font-family='Arial' font-size='20' fill='#000'>Medical</text>
              <text x='10' y='60' font-family='Arial' font-size='20' fill='#000'>Store</text>
            </svg>
            """
            response = make_response(svg)
            response.headers['Content-Type'] = 'image/svg+xml'
            return response
    
    return send_from_directory('static', 'logo.png')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Initialize database and create admin user
def create_tables():
    with app.app_context():
        # If an existing SQLite database has an older schema, drop it to avoid
        # OperationalError due to missing columns. This is safe for development
        # but will erase existing data. If you want to preserve data, use a
        # proper migration tool (Flask-Migrate / Alembic) instead.
        db_path = os.path.join(os.getcwd(), 'medical_store.db')
        if os.path.exists(db_path):
            try:
                # Quick heuristic: attempt a harmless query to see if schema is compatible
                Supplier.query.limit(1).all()
            except Exception:
                print(f"Detected incompatible DB schema at {db_path}, recreating database...")
                try:
                    os.remove(db_path)
                except Exception as e:
                    print(f"Failed to remove old database: {e}")
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='Piyu').first()
        if not admin:
            # Use a secure PBKDF2 method compatible with Werkzeug >= 2.1 / 3.x
            hashed_password = generate_password_hash('Piyu24', method='pbkdf2:sha256')
            admin = User(username='Piyu', password_hash=hashed_password, is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            # Update existing admin password
            admin.username = 'Piyu'
            # Update admin password using a compatible hashing method
            admin.password_hash = generate_password_hash('Piyu24', method='pbkdf2:sha256')
            db.session.commit()
            print("Admin credentials updated successfully!")
        
        # Create a sample supplier if none exists
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
            print("Sample supplier created successfully!")
    app.run(debug=True)
