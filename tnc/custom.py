# import frappe
# import random

# @frappe.whitelist()
# def generate_barcode(name):

# 	if self.barcode:
# 		if self.barcode == "auto":
# 			existing = frappe.db.sql_list("select barcode from tabItem")
# 			self.barcode = random.choice([item for item in map(str, range(1000,10000)) if item not in existing])
# # 			..
# ..