from django.test import TestCase, Client
from django.conf import settings

import csv, json, os, uuid
from datetime import datetime, timedelta

from .models import Transaction
from .views import TransactionView

class TransactionTest(TestCase):
	def _is_transaction_view_ok(self, singe_response):
		self.assertEqual(len(singe_response), 5)
		self.assertTrue('id' in singe_response)
		self.assertTrue('expense_type' in singe_response)
		self.assertTrue('amount' in singe_response)
		self.assertTrue('expense_date' in singe_response)
		self.assertTrue('account_id' in singe_response)

	def setUp(self):
		self.client = Client()
		self.loaded_objects = 0
		self.a_seed = []

		with open(os.path.join(os.path.dirname(__file__), 'static/db_init.csv')) as f:
			reader = csv.reader(f)

			for row in reader:
				Transaction.objects.create(
					id = row[0],
					expense_date = row[1],
					expense_type = row[2],
					amount = row[3],
					account_id = row[4]
				)
				
				self.loaded_objects += 1

				if self.loaded_objects == 1:
					self.a_seed = {
						'id' : row[0],
						'expense_date' : row[1],
						'expense_type' : row[2],
						'amount' : row[3],
						'account_id' : row[4]
					}

	def test_transactions_list_all(self):
		response = self.client.get('/transactions/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response_parsed), self.loaded_objects)

	def test_transactions_list_all_response_view(self):
		response = self.client.get('/transactions/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self._is_transaction_view_ok(response_parsed[0])

	def test_transactions_list_one_response_view(self):
		response = self.client.get('/transactions/' + self.a_seed['id'] + '/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self._is_transaction_view_ok(response_parsed)

	def test_transactions_list_one_response_invalid(self):
		response = self.client.get('/transactions/00000000-0000-0000-0000-000000000000/')

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, b'')

	def test_transactions_delete(self):
		"""Given a unique transaction ID, the corresponding record should be soft deleted."""

		response = self.client.delete('/transactions/' + self.a_seed['id'] + '/')

		self.assertEqual(response.status_code, 204)
		self.assertEqual(response.content, b'')


	def test_transactions_delete_invalid(self):
		response = self.client.delete('/transactions/00000000-0000-0000-0000-000000000000/')

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, b'')

	def test_transactions_delete_no_uuid(self):
		response = self.client.delete('/transactions/')

		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content, b'')

	def test_transactions_add(self):
		"""Given an expense_type, amount, date and account_id a new transaction is created and its unique ID is returned."""

		self.assertEqual(len(Transaction.ExpenseType.choices), 5)

		for expense_type in ['invoice', 'salary', 'services', 'office-supplies', 'travel']:
			post_content = {
				'expense_type' : expense_type,
				'amount' : 100.00,
				'expense_date' : '1234-12-12',
				'account_id' : '00000000-0000-0000-0000-000000000000'
			}

			response = self.client.post('/transactions/', post_content)
			response_parsed = json.loads(response.content)

			self.assertEqual(response.status_code, 201)
			self.assertTrue(len(response_parsed), 1)
			self.assertTrue('id' in response_parsed)

	def test_transactions_add_ivalid_expense_type(self):
		post_content = {
			'expense_type' : 'invalid_expense_type',
			'amount' : 1000.00,
			'expense_date' : '1234-12-12',
			'account_id' : '00000000-0000-0000-0000-000000000000'
		}

		response = self.client.post('/transactions/', post_content)

		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content, b'')

	def test_transactions_add_ivalid_amount(self):
		post_content = {
			'expense_type' : 'invoice',
			'amount' : 10000000000.00,
			'expense_date' : '1234-12-12',
			'account_id' : '00000000-0000-0000-0000-000000000000'
		}

		response = self.client.post('/transactions/', post_content)

		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content, b'')

	def test_transactions_add_ivalid_expense_date(self):
		post_content = {
			'expense_type' : 'invoice',
			'amount' : 1000.00,
			'expense_date' : 'invalid_expense_date',
			'account_id' : '00000000-0000-0000-0000-000000000000'
		}

		response = self.client.post('/transactions/', post_content)

		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content, b'')

	def test_transactions_add_ivalid_expense_date(self):
		post_content = {
			'expense_type' : 'invoice',
			'amount' : 1000.00,
			'expense_date' : '1234-12-12',
			'account_id' : 'invalid_account_id'
		}

		response = self.client.post('/transactions/', post_content)

		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.content, b'')

class BreakdownTest(TestCase):
	def _transactions_sum_from_to_by_type(self, date_from, date_to):
		res_sum_by_type = {}

		for expense_type_choices in Transaction.ExpenseType.choices:
			res_sum_by_type[expense_type_choices[0]] = 0

		for transaction in self.transactions:
			if date_from <= transaction['expense_date'] and transaction['expense_date'] <= date_to:
				res_sum_by_type[transaction['expense_type']] += transaction['amount']

		return res_sum_by_type

	def _check_expense_type_sums(self, response_parsed, date_from, date_to):
		expenses_by_type = self._transactions_sum_from_to_by_type(date_from, date_to)

		for expense_type_choices in Transaction.ExpenseType.choices:
			expense_type = expense_type_choices[0]
			self.assertEqual(response_parsed[expense_type]['sum'], expenses_by_type[expense_type])

	def setUp(self):
		self.client = Client()
		self.account_id = ''
		self.transactions = []
		self.date_min = datetime.now().date()
		self.date_max = datetime(1, 1, 1).date()

		with open(os.path.join(os.path.dirname(__file__), 'static/db_init.csv')) as f:
			reader = csv.reader(f)
			is_first = True

			for row in reader:
				Transaction.objects.create(
					id = row[0],
					expense_date = row[1],
					expense_type = row[2],
					amount = row[3],
					account_id = row[4]
				)

				if is_first == 1:
					is_first = False
					self.account_id = row[4]
				
				if row[4] == self.account_id:
					dt = datetime.strptime(row[1], settings.DATE_FORMAT).date()

					if dt < self.date_min:
						self.date_min = dt

					if dt > self.date_max:
						self.date_max = dt

					self.transactions.append({
						'expense_date' : dt,
						'amount' : float(row[3]),
						'expense_type' : row[2]
					})

	def test_account_breakdown_all(self):
		"""If no date range is provided, the endpoint should return a breakdown for the entire available period."""

		date_from = datetime(1, 1, 1).date()
		date_to = datetime.now().date()

		response = self.client.get('/accounts/' + self.account_id + '/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self._check_expense_type_sums(response_parsed, date_from, date_to)

	def test_account_breakdown_from(self):
		date_from = self.date_min + timedelta(days=1)
		date_to = datetime.now().date()

		response = self.client.get('/accounts/' + self.account_id + '/' + date_from.strftime(settings.DATE_FORMAT) + '/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self._check_expense_type_sums(response_parsed, date_from, date_to)

	def test_account_breakdown_from_to(self):
		"""Given an account_id and a date range, find the sum and count of transactions for each expense type."""

		date_from = self.date_min + timedelta(days=1)
		date_to = self.date_max - timedelta(days=1)

		response = self.client.get('/accounts/' + self.account_id + '/' + date_from.strftime(settings.DATE_FORMAT) + '/' + date_to.strftime(settings.DATE_FORMAT) + '/')
		response_parsed = json.loads(response.content)

		self.assertEqual(response.status_code, 200)
		self._check_expense_type_sums(response_parsed, date_from, date_to)
