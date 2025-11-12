import app as app_module
from datetime import datetime, timedelta

app = app_module.app
app.testing = True

def post(client, path, data, follow=False):
    return client.post(path, data=data, follow_redirects=follow)

def main():
    with app.test_client() as client:
        # Login
        r = post(client, '/login', {'username':'Piyu','password':'Piyu24'}, follow=True)
        print('Login status', r.status_code)

        # Create a supplier
        supplier_data = {
            'name': 'Automated Supplier',
            'contact': 'Auto',
            'email': 'auto@supplier.test',
            'phone': '+1000000000',
            'address': '123 Auto St',
            'gst_number': '22AUTO0000A1Z1'
        }
        r = post(client, '/supplier/add', supplier_data, follow=True)
        print('/supplier/add ->', r.status_code)

        # Get suppliers page and find the new supplier id by searching the HTML
        resp = client.get('/suppliers')
        html = resp.data.decode('utf-8')
        print('/suppliers ->', resp.status_code)
        # crude parse: find last occurrence of view_supplier link
        import re
        m = re.search(r"/supplier/(\d+)", html)
        supplier_id = m.group(1) if m else None
        print('Discovered supplier id:', supplier_id)

        # Add a medicine linked to that supplier
        expiry = (datetime.utcnow() + timedelta(days=365)).strftime('%Y-%m-%d')
        med_data = {
            'name': 'TestMed',
            'description': 'Test medicine',
            'quantity': '10',
            'price': '9.99',
            'supplier_id': supplier_id or '',
            'expiry_date': expiry,
            'batch_number': 'BATCH1'
        }
        r = post(client, '/add_medicine', med_data, follow=True)
        print('/add_medicine ->', r.status_code)

        # Get medicines and find medicine id
        resp = client.get('/medicines')
        html = resp.data.decode('utf-8')
        print('/medicines ->', resp.status_code)
        # simpler: find first numeric id in medicines table
        ids = re.findall(r"<td>(\d+)</td>", html)
        medicine_id = ids[0] if ids else None
        print('Discovered medicine id:', medicine_id)

        # Create a sale for that medicine
        if medicine_id:
            from werkzeug.datastructures import MultiDict
            sale_data = MultiDict([
                ('customer_name','Test Customer'),
                ('customer_contact','+1999999999'),
                ('payment_method','Cash'),
                ('discount','0'),
                ('tax_percentage','0'),
                ('medicine_id[]', medicine_id),
                ('quantity[]', '2'),
                ('price[]', '9.99')
            ])
            r = client.post('/sale/new', data=sale_data, follow_redirects=True)
            print('/sale/new ->', r.status_code)
            # After sale, check sales list
            resp = client.get('/sales')
            print('/sales ->', resp.status_code)
        else:
            print('Could not determine medicine id; skipping sale step')

if __name__ == '__main__':
    main()
