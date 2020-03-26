from django.test import TestCase
from django.test import TransactionTestCase
# from payments.models import Transactions
# from payments.models import ExtraDetails
from django.test import Client


class TransactionsTestCase(TransactionTestCase):

    def setUp(self):
        c = Client()
        response = c.post('/api/client-collections/v1/transactions/submit/',
                          {'payer': 'ABC',
                           'payer_msisdn': '233456789',
                           'narration': 'My payment',
                           'reference_number': 'x1y2z3',
                           'account_number': '233555009988',
                           'amount': 1, 'provider': 'MTN MOBILE MONEY',
                           'extra_details': {
                               'resident': '7',
                               'ccu_license_no': '34r8989j792nfv'
                           }
                           },
                          'application/json'
                          )

        self.assertEqual(response.status_code, 200)
        p_stat = response.json()['status']
        self.assertEqual(p_stat, 201)

    def test_transaction_duplicate_post(self):
        c = Client()
        response = c.post('/api/client-collections/v1/transactions/submit/',
                          {'payer': 'ABC',
                           'payer_msisdn':'2334567899',
                           'narration': 'My payment',
                           'reference_number': 'x1y2z3',
                           'account_number': '233555009988',
                           'amount': 1, 'provider': 'MTN MOBILE MONEY',
                           'extra_details': {
                               'resident': '7',
                               'ccu_license_no': '34r8989j792nfv'
                           }
                           },
                          'application/json'
                          )

    #     self.assertEqual(response.status_code, 200)
    #     p_stat = response.json()['status']
    #     print(response.json()['status'])
    #     self.assertEqual(p_stat, 900)
    #
    # def test_transaction_check(self):
    #     c = Client()
    #     response = c.get('/api/client-collections/v1/transactions/search/payer_reference/x1y2z3/')
    #     self.assertEqual(response.status_code, 200)
    #     print(f"{response.json()}")
    #     p_stat = response.json()['transaction_status']
    #     self.assertEqual(p_stat, 'PENDING')
    #
    # def test_transaction_update(self):
    #     c = Client()
    #     response = c.post('/api/client-collections/v1/transactions/update/payer_reference/x1y2z3/',
    #                        {'status': 'PAID'},
    #                        'application/json'
    #                        )
    #     self.assertEqual(response.status_code, 200)
    #     print(f"{response.json()}")
    #     p_stat = response.json()['status']
    #     self.assertEqual(p_stat, 200)
    #
    # def test_transaction_search_check(self):
    #     c = Client()
    #     response = c.get('/api/client-collections/v1/transactions/search/payer_reference/x1y2z3/')
    #     self.assertEqual(response.status_code, 200)
    #     print(f"{response.json()}")
    #     p_stat = response.json()['transaction_status']
    #     self.assertEqual(p_stat, "PAID")
    #
    # def test_transaction_list(self):
    #     c = Client()
    #     response = c.get('/api/client-collections/v1/transactions/list/')
    #     self.assertEqual(response.status_code, 200)
    #     print(f"{response.json()}")
    #     p_stat = response.json()['status']
    #     self.assertEqual(p_stat, 200)
