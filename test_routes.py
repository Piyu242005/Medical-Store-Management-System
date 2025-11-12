import traceback
import sys
import app as app_module


def check_route(client, method, path, **kwargs):
    try:
        if method == 'GET':
            resp = client.get(path, **kwargs)
        elif method == 'POST':
            resp = client.post(path, **kwargs)
        else:
            print(f'Unsupported method {method} for {path}')
            return True

        print(f'{method} {path} -> {resp.status_code}')
        if resp.status_code >= 500:
            print('Response body (truncated):')
            print(resp.data.decode('utf-8')[:1000])
            return False
        return True
    except Exception:
        print(f'Exception when requesting {path}:')
        traceback.print_exc()
        return False


def main():
    app = app_module.app
    app.testing = True

    with app.test_client() as client:
        # Login
        print('Logging in...')
        login = client.post('/login', data={'username': 'Piyu', 'password': 'Piyu24'}, follow_redirects=True)
        print('Login status:', login.status_code)

        routes = [
            ('GET', '/'),
            ('GET', '/dashboard'),
            ('GET', '/medicines'),
            ('GET', '/medicines?page=1'),
            ('GET', '/add_medicine'),
            ('GET', '/suppliers'),
            ('GET', '/supplier/add'),
            ('GET', '/sales'),
            ('GET', '/sale/new'),
            ('GET', '/reports'),
            ('GET', '/export/report/sales'),
            ('GET', '/export/report/inventory'),
        ]

        all_ok = True
        for method, path in routes:
            ok = check_route(client, method, path)
            if not ok:
                all_ok = False

        if all_ok:
            print('\nAll tested routes returned non-500 status codes.')
            sys.exit(0)
        else:
            print('\nSome routes failed. See output above.')
            sys.exit(2)


if __name__ == '__main__':
    main()
