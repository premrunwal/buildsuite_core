import frappe
from frappe import _


@frappe.whitelist(allow_guest=True, methods=["POST"])
def mobile_login(usr=None, pwd=None):
	"""Single-request authentication endpoint for mobile app.

	Takes username & password, authenticates the user, ensures they have
	BuildSuite Core permissions, creates or fetches their API key/secret,
	and returns credentials in a single response without relying on session cookies.
	"""
	data = frappe.form_dict
	usr = usr or data.get("usr") or data.get("username")
	pwd = pwd or data.get("pwd") or data.get("password")

	if not usr or not pwd:
		frappe.throw(_("Username and password are required"), frappe.AuthenticationError)

	login_manager = frappe.auth.LoginManager()
	login_manager.authenticate(user=usr, pwd=pwd)
	user = login_manager.user

	# Switch session user to the authenticated user for permissions & doc operations
	frappe.set_user(user)

	from buildsuite_core.api.permission import ALLOWED_ROLES

	user_roles = set(frappe.get_roles(user))
	if (
		user != "Administrator"
		and not user_roles.intersection(ALLOWED_ROLES)
		and "Administrator" not in user_roles
		and "System Manager" not in user_roles
	):
		frappe.throw(
			_("User does not have permission to access BuildSuite Core"),
			frappe.PermissionError,
		)

	user_doc = frappe.get_doc("User", user)
	api_secret = None

	if not user_doc.api_key:
		user_doc.set_api_key()
		api_secret = user_doc.set_api_secret()
		user_doc.save(ignore_permissions=True)
	else:
		try:
			api_secret = user_doc.get_password("api_secret")
		except Exception:
			api_secret = None

		if not api_secret:
			api_secret = user_doc.set_api_secret()
			user_doc.save(ignore_permissions=True)

	frappe.db.commit()

	return {
		"user": user,
		"full_name": user_doc.full_name or user,
		"api_key": user_doc.api_key,
		"api_secret": api_secret,
	}


@frappe.whitelist(methods=["POST"])
def get_or_create_api_keys():
	"""Whitelisted endpoint for authenticated mobile app users to obtain API Key & Secret."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	user = frappe.session.user
	from buildsuite_core.api.permission import ALLOWED_ROLES

	user_roles = set(frappe.get_roles(user))
	if (
		user != "Administrator"
		and not user_roles.intersection(ALLOWED_ROLES)
		and "Administrator" not in user_roles
		and "System Manager" not in user_roles
	):
		frappe.throw(
			_("User does not have permission to access BuildSuite Core"),
			frappe.PermissionError,
		)

	user_doc = frappe.get_doc("User", user)
	api_secret = None

	if not user_doc.api_key:
		user_doc.set_api_key()
		api_secret = user_doc.set_api_secret()
		user_doc.save(ignore_permissions=True)
	else:
		try:
			api_secret = user_doc.get_password("api_secret")
		except Exception:
			api_secret = None

		if not api_secret:
			api_secret = user_doc.set_api_secret()
			user_doc.save(ignore_permissions=True)

	frappe.db.commit()

	return {
		"user": user,
		"full_name": user_doc.full_name or user,
		"api_key": user_doc.api_key,
		"api_secret": api_secret,
	}
