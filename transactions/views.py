from django.shortcuts import render
from django.db.models import Sum
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import datetime

from .models import Transaction
from .serializers import TransactionSerializerSingle

class DefaultView(APIView):
	def get(self, request):
		return Response({'message' : 'did you read the readme?'}, 400)

class TransactionView(APIView):
	def post(self, request):
		transaction = TransactionSerializerSingle(data=request.data)

		if transaction.is_valid():
			transaction_item = transaction.save()
			return Response({'id' : transaction_item.id}, status=201)

		return Response(None, status=422)

	def get(self, request, transaction_id=None):
		request_all = transaction_id is None

		if request_all:
			transactions = Transaction.objects.all()
		else:
			try:
				transactions = Transaction.objects.get(pk=transaction_id)
			except Transaction.DoesNotExist:
				return Response(None, status=400)
		
		transactions_data = TransactionSerializerSingle(transactions, many=request_all)

		return Response(transactions_data.data, status=200)

	def delete(self, request, transaction_id=None):
		if transaction_id is None:
			return Response(None, status=400)

		try:
			transaction = Transaction.objects.get(pk=transaction_id)
		except Transaction.DoesNotExist:
			return Response(None, status=400)

		transaction.delete()

		return Response(None, status=204)

class AccountBreakdown(APIView):
	def get(self, request, account_id, date_from=None, date_to=None):
		response = {
			'account_id' : account_id,
			'date_from' : date_from,
			'date_to' : date_to,
		}

		if date_from is None:
			transactions = Transaction.objects.filter(account_id=account_id)

			date_from = datetime(1, 1, 1).date()
			date_to = datetime.now().date()
		else:
			date_from = datetime.strptime(date_from, settings.DATE_FORMAT).date()

			if date_to is None:
				transactions = Transaction.objects.filter(account_id=account_id, expense_date__gte=date_from)

				date_to = datetime.now().date()
			else:
				date_to = datetime.strptime(date_to, settings.DATE_FORMAT).date()

				transactions = Transaction.objects.filter(account_id=account_id, expense_date__gte=date_from, expense_date__lte=date_to)


		for expense_type_choises in Transaction.ExpenseType.choices:
			expense_type = expense_type_choises[0]
			transactions_filtered = transactions.filter(expense_type=expense_type)

			transactions_count = transactions_filtered.count()
			transactions_sum = transactions_filtered.aggregate(sum=Sum('amount'))['sum'] or 0

			response[expense_type] = {
				'sum' : transactions_sum,
				'count' : transactions_count
			}

		return Response(response, status=200)
