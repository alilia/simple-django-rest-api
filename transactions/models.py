from django.db import models
from django.utils.timezone import now

from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE

import uuid
from datetime import date

class Transaction(SafeDeleteModel):
	_safedelete_policy = SOFT_DELETE

	class ExpenseType(models.TextChoices):
		INVOICE = 'invoice'
		SALARY = 'salary'
		SERVICES = 'services'
		OFFICE_SUPPLIES = 'office-supplies'
		TRAVEL = 'travel'

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	expense_type = models.CharField(
		max_length=15,
		choices=ExpenseType.choices,
		default=ExpenseType.INVOICE
	)
	amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	expense_date = models.DateField(default=now)
	account_id = models.UUIDField()
