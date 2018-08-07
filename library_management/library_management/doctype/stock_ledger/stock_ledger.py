# -*- coding: utf-8 -*-
# Copyright (c) 2018, Ayushi Patel and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StockLedger(Document):
	pass




@frappe.whitelist()
def StockEntry(doc,method):
	stock_ledger=frappe.new_doc('Stock Ledger')
	stock_ledger.voucher_name = doc.doctype
	stock_ledger.voucher_no = doc.name
	stock_ledger.insert()
	

	
