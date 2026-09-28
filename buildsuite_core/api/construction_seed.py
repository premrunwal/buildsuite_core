import frappe
from frappe import _
from frappe.utils.password import set_encrypted_password


DEFAULT_SEED_PASSWORD = "admin"

PERSONAS_USERS = [
	("director@buildsuite.site", "Dana", "Director", "Director / Owner", "BuildSuite Director"),
	("pm@buildsuite.site", "Paul", "Manager", "Project Manager", "BuildSuite PM"),
	("site.engineer@buildsuite.site", "Sam", "Engineer", "Site Engineer", "BuildSuite Site Engineer"),
	("supervisor@buildsuite.site", "Frank", "Foreman", "Foreman / Supervisor", "BuildSuite Foreman"),
	("procurement@buildsuite.site", "Perry", "Procurement", "Procurement Officer", "BuildSuite Procurement Officer"),
	("storekeeper@buildsuite.site", "Steve", "Storekeeper", "Store Keeper", "BuildSuite Store Keeper"),
	("qs@buildsuite.site", "Quinn", "Surveyor", "Quantity Surveyor", "BuildSuite QS"),
	("estimator@buildsuite.site", "Esther", "Estimator", "Estimator", "BuildSuite Estimator"),
	("accountant@buildsuite.site", "Alice", "Accountant", "Accountant", "BuildSuite Accountant"),
	("hr@buildsuite.site", "Helen", "HR", "HR Manager", "BuildSuite HR Manager"),
]

UOMS = [
	"Bag",
	"Kg",
	"Metric Ton",
	"Cubic Meter",
	"Square Meter",
	"Nos",
	"Liter",
	"Meter",
	"Sheet",
	"Drum",
	"Box",
]

ITEM_GROUPS = [
	("Raw Material", "All Item Groups"),
	("Cement", "Raw Material"),
	("Steel & Rebar", "Raw Material"),
	("Aggregates & Sand", "Raw Material"),
	("Masonry & Blocks", "Raw Material"),
	("Piping & Electrical", "All Item Groups"),
	("Formwork & Consumables", "All Item Groups"),
]

# (item_code, item_name, item_group, stock_uom, rate_code, rate_name, category, default_rate)
MATERIALS = [
	# Cement
	(
		"MAT-CEM-JK-53",
		"JK Super Cement OPC 53 Grade (50kg)",
		"Cement",
		"Bag",
		"CEM-JK-53",
		"JK Super Cement OPC 53 Grade",
		"Material",
		390.00,
	),
	(
		"MAT-CEM-BIRLA-PPC",
		"Birla A1 Cement PPC (50kg)",
		"Cement",
		"Bag",
		"CEM-BIRLA-PPC",
		"Birla A1 Cement PPC",
		"Material",
		375.00,
	),
	(
		"MAT-CEM-ULTRATECH",
		"UltraTech Super Cement (50kg)",
		"Cement",
		"Bag",
		"CEM-ULTRATECH",
		"UltraTech Super Cement PPC",
		"Material",
		410.00,
	),
	(
		"MAT-CEM-AMBUJA",
		"Ambuja Plus Roof Special Cement (50kg)",
		"Cement",
		"Bag",
		"CEM-AMBUJA",
		"Ambuja Plus Roof Special Cement",
		"Material",
		425.00,
	),
	# Steel & TMT Rebar (8mm, 10mm, 12mm, 16mm branded)
	(
		"MAT-STL-TATA-8MM",
		"Tata Tiscon 550D TMT Bar 8mm",
		"Steel & Rebar",
		"Kg",
		"STL-TATA-8MM",
		"Tata Tiscon 550D Rebar 8mm",
		"Material",
		72.50,
	),
	(
		"MAT-STL-TATA-10MM",
		"Tata Tiscon 550D TMT Bar 10mm",
		"Steel & Rebar",
		"Kg",
		"STL-TATA-10MM",
		"Tata Tiscon 550D Rebar 10mm",
		"Material",
		71.00,
	),
	(
		"MAT-STL-TATA-12MM",
		"Tata Tiscon 550D TMT Bar 12mm",
		"Steel & Rebar",
		"Kg",
		"STL-TATA-12MM",
		"Tata Tiscon 550D Rebar 12mm",
		"Material",
		69.50,
	),
	(
		"MAT-STL-TATA-16MM",
		"Tata Tiscon 550D TMT Bar 16mm",
		"Steel & Rebar",
		"Kg",
		"STL-TATA-16MM",
		"Tata Tiscon 550D Rebar 16mm",
		"Material",
		69.50,
	),
	(
		"MAT-STL-JSW-8MM",
		"JSW Neosteel 550D TMT Bar 8mm",
		"Steel & Rebar",
		"Kg",
		"STL-JSW-8MM",
		"JSW Neosteel 550D Rebar 8mm",
		"Material",
		68.00,
	),
	(
		"MAT-STL-JSW-16MM",
		"JSW Neosteel 550D TMT Bar 16mm",
		"Steel & Rebar",
		"Kg",
		"STL-JSW-16MM",
		"JSW Neosteel 550D Rebar 16mm",
		"Material",
		66.50,
	),
	(
		"MAT-STL-JINDAL-8MM",
		"Jindal Panther 550D TMT Bar 8mm",
		"Steel & Rebar",
		"Kg",
		"STL-JINDAL-8MM",
		"Jindal Panther 550D Rebar 8mm",
		"Material",
		67.00,
	),
	(
		"MAT-STL-JINDAL-16MM",
		"Jindal Panther 550D TMT Bar 16mm",
		"Steel & Rebar",
		"Kg",
		"STL-JINDAL-16MM",
		"Jindal Panther 550D Rebar 16mm",
		"Material",
		65.50,
	),
	(
		"MAT-STL-BINDING-18G",
		"GI Binding Wire 18 Gauge",
		"Steel & Rebar",
		"Kg",
		"STL-BINDING-18G",
		"GI Binding Wire 18 Gauge",
		"Material",
		85.00,
	),
	# Aggregates & Sand
	(
		"MAT-SND-RIVER",
		"River Sand (Coarse / Concrete Grade)",
		"Aggregates & Sand",
		"Cubic Meter",
		"SND-RIVER",
		"River Sand (Coarse Concrete)",
		"Material",
		1650.00,
	),
	(
		"MAT-SND-MSAND",
		"Manufactured M-Sand (Plastering Grade)",
		"Aggregates & Sand",
		"Cubic Meter",
		"SND-MSAND",
		"Manufactured M-Sand",
		"Material",
		1100.00,
	),
	(
		"MAT-AGG-10MM",
		"Coarse Aggregate 10mm (Blue Metal)",
		"Aggregates & Sand",
		"Cubic Meter",
		"AGG-10MM",
		"Coarse Aggregate 10mm",
		"Material",
		950.00,
	),
	(
		"MAT-AGG-20MM",
		"Coarse Aggregate 20mm (Blue Metal)",
		"Aggregates & Sand",
		"Cubic Meter",
		"AGG-20MM",
		"Coarse Aggregate 20mm",
		"Material",
		900.00,
	),
	(
		"MAT-AGG-QUARRY-DUST",
		"Quarry Stone Dust",
		"Aggregates & Sand",
		"Cubic Meter",
		"AGG-QUARRY-DUST",
		"Quarry Stone Dust",
		"Material",
		650.00,
	),
	# Masonry & Blocks
	(
		"MAT-BLK-RED-CLAY",
		"Red Clay Wire-Cut Bricks (9x4x3 inch)",
		"Masonry & Blocks",
		"Nos",
		"BLK-RED-CLAY",
		"Red Clay Wire-Cut Bricks",
		"Material",
		9.50,
	),
	(
		"MAT-BLK-AAC-150",
		"AAC Lightweight Blocks (600x200x150mm)",
		"Masonry & Blocks",
		"Nos",
		"BLK-AAC-150",
		"AAC Blocks 600x200x150mm",
		"Material",
		62.00,
	),
	(
		"MAT-BLK-CONC-6IN",
		"Solid Concrete Blocks 6 inch",
		"Masonry & Blocks",
		"Nos",
		"BLK-CONC-6IN",
		"Solid Concrete Blocks 6 inch",
		"Material",
		38.00,
	),
	# Piping & Electrical
	(
		"MAT-PIP-PVC-4IN",
		"Supreme PVC Pipe 4 inch 6kg/cm2 (6m)",
		"Piping & Electrical",
		"Nos",
		"PIP-PVC-4IN",
		"Supreme PVC Pipe 4 inch",
		"Material",
		820.00,
	),
	(
		"MAT-ELE-CONDUIT-25",
		"Finolex Rigid PVC Conduit Pipe 25mm",
		"Piping & Electrical",
		"Meter",
		"ELE-CONDUIT-25",
		"Finolex Conduit Pipe 25mm",
		"Material",
		32.00,
	),
	# Formwork & Site Consumables
	(
		"MAT-PLY-SHUTTER-12",
		"Marine Waterproof Shuttering Plywood 12mm",
		"Formwork & Consumables",
		"Sheet",
		"PLY-SHUTTER-12",
		"Marine Shuttering Plywood 12mm",
		"Material",
		1850.00,
	),
	(
		"MAT-CHM-SHUTTER-OIL",
		"Shuttering Oil Formwork Release Agent",
		"Formwork & Consumables",
		"Liter",
		"CHM-SHUTTER-OIL",
		"Shuttering Release Oil",
		"Material",
		140.00,
	),
	(
		"MAT-CHM-WATERPROOF-LW",
		"Dr. Fixit 101 LW+ Waterproofing Liquid",
		"Formwork & Consumables",
		"Liter",
		"CHM-WATERPROOF-LW",
		"Dr. Fixit 101 LW+ Liquid",
		"Material",
		175.00,
	),
]


def _ensure_uoms():
	for name in UOMS:
		if not frappe.db.exists("UOM", name):
			frappe.get_doc({"doctype": "UOM", "uom_name": name, "enabled": 1}).insert(ignore_permissions=True)


def _ensure_item_groups():
	for group_name, parent_group in ITEM_GROUPS:
		if not frappe.db.exists("Item Group", group_name):
			parent = parent_group if frappe.db.exists("Item Group", parent_group) else "All Item Groups"
			if not frappe.db.exists("Item Group", "All Item Groups"):
				frappe.get_doc(
					{"doctype": "Item Group", "item_group_name": "All Item Groups", "is_group": 1}
				).insert(ignore_permissions=True)
			frappe.get_doc(
				{
					"doctype": "Item Group",
					"item_group_name": group_name,
					"parent_item_group": parent,
					"is_group": 0,
				}
			).insert(ignore_permissions=True)


def _seed_materials():
	_ensure_uoms()
	_ensure_item_groups()

	created_items = []
	created_rates = []

	for (
		item_code,
		item_name,
		item_group,
		stock_uom,
		rate_code,
		rate_name,
		category,
		default_rate,
	) in MATERIALS:
		# 1. Construction Rate Master
		if not frappe.db.exists("Construction Rate Master", rate_code):
			rate_doc = frappe.get_doc(
				{
					"doctype": "Construction Rate Master",
					"rate_code": rate_code,
					"rate_name": rate_name,
					"category": category,
					"uom": stock_uom,
					"current_rate": default_rate,
				}
			)
			rate_doc.insert(ignore_permissions=True)
			created_rates.append(rate_code)

		# 2. ERPNext Item
		if not frappe.db.exists("Item", item_code):
			item_doc = frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_name,
					"item_group": item_group if frappe.db.exists("Item Group", item_group) else "All Item Groups",
					"stock_uom": stock_uom,
					"is_stock_item": 1,
					"is_purchase_item": 1,
					"valuation_rate": default_rate,
					"standard_rate": default_rate,
					"custom_rate_master": rate_code,
				}
			)
			item_doc.insert(ignore_permissions=True)
			created_items.append(item_code)
		else:
			frappe.db.set_value("Item", item_code, "custom_rate_master", rate_code)

	return created_items, created_rates


def _seed_personas_and_users():
	from buildsuite_core.buildsuite_core.doctype.persona.seed_personas import seed_personas

	seed_personas()

	created_users = []
	for email, first_name, last_name, persona, role in PERSONAS_USERS:
		if frappe.db.exists("User", email):
			user_doc = frappe.get_doc("User", email)
			user_doc.enabled = 1
			user_doc.persona = persona
			user_doc.first_name = first_name
			user_doc.last_name = last_name
			if not user_doc.api_key:
				user_doc.api_key = frappe.generate_hash(length=15)
		else:
			api_key = frappe.generate_hash(length=15)
			user_doc = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": first_name,
					"last_name": last_name,
					"enabled": 1,
					"send_welcome_email": 0,
					"persona": persona,
					"new_password": DEFAULT_SEED_PASSWORD,
					"api_key": api_key,
				}
			)
			user_doc.flags.ignore_password_policy = True
			user_doc.insert(ignore_permissions=True)

		# Ensure API Secret is set
		api_secret = frappe.generate_hash(length=15)
		try:
			set_encrypted_password("User", email, api_secret, fieldname="api_secret")
		except Exception:
			pass

		# Ensure roles
		if frappe.db.exists("Role", role):
			user_doc.add_roles(role)
		if frappe.db.exists("Role", "BuildSuite Project User"):
			user_doc.add_roles("BuildSuite Project User")

		user_doc.save(ignore_permissions=True)
		created_users.append(email)

	return created_users


def _enable_emails():
	"""Ensure system email sending is enabled."""
	try:
		if frappe.db.exists("DocType", "System Settings"):
			frappe.db.set_value("System Settings", None, "disable_email_communication", 0)
			frappe.db.set_value("System Settings", None, "enable_password_policy", 0)
	except Exception:
		pass


@frappe.whitelist()
def seed_construction_data():
	"""Main entry point to seed construction materials, inventory, personas, users, and enable emails."""
	# Suppress background-job enqueueing so this works without Redis
	_prev_in_import = getattr(frappe.flags, "in_import", False)
	frappe.flags.in_import = True
	try:
		users = _seed_personas_and_users()
		items, rates = _seed_materials()
		_enable_emails()
		frappe.db.commit()
	finally:
		frappe.flags.in_import = _prev_in_import

	summary = {
		"status": "success",
		"message": "Construction site materials, inventory, personas, and emails configured successfully.",
		"users_seeded": len(users),
		"users": users,
		"default_password": DEFAULT_SEED_PASSWORD,
		"materials_seeded": len(items),
		"rate_masters_seeded": len(rates),
		"emails_enabled": True,
	}
	print(frappe.as_json(summary))
	return summary
