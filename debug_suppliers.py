import traceback
import sys
import os

# Import the app and use the Flask test client to reproduce the error
import app as app_module

def main():
    app = app_module.app
    # Enable testing so exceptions propagate to the test client
    app.testing = True

    with app.test_client() as client:
        try:
            # First, login using seeded admin credentials
            login_resp = client.post('/login', data={'username': 'Piyu', 'password': 'Piyu24'}, follow_redirects=True)
            print('Login response status:', login_resp.status_code)

            # Now request the suppliers page
            resp = client.get('/suppliers')
            print('Suppliers response status:', resp.status_code)
            # If no exception raised, print small part of the HTML to inspect
            print(resp.data.decode('utf-8')[:1000])

        except Exception:
            print('Exception when requesting /suppliers:')
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
