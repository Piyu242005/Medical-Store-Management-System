import sys
import traceback
import app as app_module

app = app_module.app
app.testing = True

routes = [
    '/',
    '/dashboard',
    '/medicines',
    '/suppliers',
    '/sales',
    '/sale/new',
    '/reports',
]

def main():
    with app.test_client() as client:
        try:
            # login
            resp = client.post('/login', data={'username': 'Piyu', 'password': 'Piyu24'}, follow_redirects=True)
            print('Login status:', resp.status_code)
            for r in routes:
                try:
                    resp = client.get(r)
                    print(f'GET {r} ->', resp.status_code)
                    if resp.status_code >= 500:
                        print('Response excerpt:\n', resp.data.decode('utf-8')[:1000])
                except Exception as e:
                    print(f'Exception when GET {r}:')
                    traceback.print_exc()
        except Exception:
            print('Error during smoke tests:')
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
