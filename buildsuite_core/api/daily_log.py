import frappe
from frappe import _
from frappe.utils import today, now, getdate


@frappe.whitelist()
def get_daily_logs(project=None, from_date=None, to_date=None, limit=20):
	"""Get daily log entries combining Task Progress Entries, Field Attendance, and Site Photos."""
	filters = {}
	if project:
		filters["project"] = project
	if from_date and to_date:
		filters["entry_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["entry_date"] = [">=", from_date]

	progress_entries = frappe.get_all(
		"Task Progress Entry",
		filters=filters,
		fields=[
			"name",
			"project",
			"entry_date",
			"progress_percentage",
			"narrative_description",
			"weather_condition",
			"blocker_flag",
			"blocker_details",
			"owner",
			"creation",
		],
		order_by="creation desc",
		limit=limit,
	)

	for entry in progress_entries:
		# Attach project name
		if entry.get("project"):
			entry["project_name"] = frappe.db.get_value("Project", entry["project"], "project_name") or entry["project"]
		
		# Get attached photos/files
		files = frappe.get_all(
			"File",
			filters={
				"attached_to_doctype": "Task Progress Entry",
				"attached_to_name": entry["name"],
			},
			fields=["name", "file_name", "file_url", "is_private"],
		)
		entry["photos"] = files

		# Get user full name
		user_info = frappe.db.get_value("User", entry["owner"], ["first_name", "last_name", "user_image"], as_dict=True)
		if user_info:
			entry["author_name"] = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip() or entry["owner"]
			entry["author_image"] = user_info.user_image
		else:
			entry["author_name"] = entry["owner"]

	return progress_entries


@frappe.whitelist()
def get_site_photos(project=None, limit=50):
	"""Get all site photos uploaded across Projects, Tasks, and Progress Entries."""
	filters = {}
	if project:
		# Get files attached to the project directly or to tasks/progress entries of the project
		progress_entry_names = frappe.get_all("Task Progress Entry", filters={"project": project}, pluck="name")
		task_names = frappe.get_all("Task", filters={"project": project}, pluck="name")
		
		or_filters = [
			["attached_to_doctype", "=", "Project"],
			["attached_to_name", "=", project],
		]
		if progress_entry_names:
			or_filters.append(["attached_to_name", "in", progress_entry_names])
		if task_names:
			or_filters.append(["attached_to_name", "in", task_names])
		
		files = frappe.get_all(
			"File",
			filters=[
				["is_folder", "=", 0],
				["file_url", "like", "%.jpg"],
			],
			or_filters=[
				["file_url", "like", "%.png"],
				["file_url", "like", "%.jpeg"],
				["file_url", "like", "%.webp"],
			],
			fields=["name", "file_name", "file_url", "attached_to_doctype", "attached_to_name", "owner", "creation"],
			order_by="creation desc",
			limit=limit,
		)
	else:
		files = frappe.get_all(
			"File",
			filters={"is_folder": 0},
			or_filters=[
				["file_url", "like", "%.jpg"],
				["file_url", "like", "%.jpeg"],
				["file_url", "like", "%.png"],
				["file_url", "like", "%.webp"],
			],
			fields=["name", "file_name", "file_url", "attached_to_doctype", "attached_to_name", "owner", "creation"],
			order_by="creation desc",
			limit=limit,
		)

	for f in files:
		user_info = frappe.db.get_value("User", f["owner"], ["first_name", "last_name"], as_dict=True)
		if user_info:
			f["uploader"] = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
		else:
			f["uploader"] = f["owner"]

	return files


@frappe.whitelist()
def create_daily_log(project, entry_date=None, weather_condition="Clear", narrative="", progress_percentage=0, blocker_flag=0, blocker_details=""):
	"""Create a new daily log / task progress entry with site details."""
	doc = frappe.get_doc({
		"doctype": "Task Progress Entry",
		"project": project,
		"entry_date": entry_date or today(),
		"weather_condition": weather_condition,
		"narrative_description": narrative,
		"progress_percentage": float(progress_percentage or 0),
		"blocker_flag": 1 if blocker_flag else 0,
		"blocker_details": blocker_details if blocker_flag else "",
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name
