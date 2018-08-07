# -*- coding: utf-8 -*-
# Copyright (c) 2018, Ayushi Patel and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.model.document import Document
import collections

class LibraryTransaction(Document):

	def validate_items_qty(self):
		total_qty=0
		for item in self.items:
			total_qty += int(item.qty)
		setting_qty = frappe.db.get_value("Library Management Settings", "Library Management Settings", "max_article_borrow_limit_per_transaction")
		setting_max_qty = frappe.db.get_value("Library Management Settings", "Library Management Settings", "max_article_borrow_limit")
		if int(total_qty) > int(setting_qty):
			frappe.throw(_("You can't select more than two item or Quantity in single  Transaction"))
		if (int(total_qty) + self.get_member_wise_issued_book(self.library_member)) > int(setting_max_qty):
			frappe.throw(_("You can't borrow more then "+setting_max_qty+" Articles"))
	
	def get_available_qty(self):
		article_wise_detail = collections.OrderedDict()
		for ledger in self.get_transaction():
			doc = frappe.get_doc(ledger.voucher_name,ledger.voucher_no)
			if doc:
				if doc.doctype=='Library Transaction' and doc.transaction_type=='Issue':
					for article in doc.items:
						if article.article in article_wise_detail:
							article_wise_detail[article.article] = article_wise_detail[article.article] - article.qty
						else:
							if article.article in article_wise_detail:
								pass
							else:
								article_wise_detail[article.article]=0
							#if 0 >= (article_wise_detail[article.article] - article.qty):
							#	frappe.throw(_("Can not return without issuing book"))
							#else:
								article_wise_detail[article.article] = article.qty
				else:
					for article in doc.items:
						if article.article in article_wise_detail:
							article_wise_detail[article.article] = article_wise_detail[article.article] + article.qty
						else:
							article_wise_detail[article.article] = article.qty
		return article_wise_detail

	def validate_stock(self):
		stocks=self.get_available_qty()
		if not self.transaction_type=='Return':
			for item in self.items:
				if item.article in stocks:
					pass
				else:
					stocks[item.article]=0
				if int(item.qty) > int(stocks[item.article]):
						frappe.throw(str(item.article)+" not available in stock. "+str(int(item.qty) - int(stocks[item.article]))+" qty required." )
			
					
	def get_transaction(self):
		return frappe.get_all('Stock Ledger',fields=['*'],filters={})


	def get_member_wise_issued_book(self,member):
		total_issue_book=0
		for issue in frappe.get_all('Library Transaction',fields=['*'],filters=[['Library Transaction Item','is_returned','=','0'],['Library Transaction','library_member','=',member],['Library Transaction','docstatus','=',1]]):
			doc = frappe.get_doc('Library Transaction',issue.name)
			for item in doc.items:
				if item.is_returned==0:
					total_issue_book += item.qty
		return total_issue_book

					

	def validate(self):
		self.validate_items_qty()
		self.validate_stock()


