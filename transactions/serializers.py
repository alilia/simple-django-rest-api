from rest_framework import serializers
from rest_framework.response import Response

from .models import Transaction

class TransactionSerializerSingle(serializers.ModelSerializer):
	class Meta:
		model = Transaction
		fields = ['id', 'expense_type', 'amount', 'expense_date', 'account_id']
