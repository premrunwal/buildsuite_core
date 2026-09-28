import frappe
from frappe import _


def _get_or_generate_api_keys(user):
	"""Safely get or generate api_key and api_secret for a user."""
	user_doc = frappe.get_doc("User", user)
	api_key = user_doc.api_key
	api_secret = None

	if api_key:
		try:
			api_secret = user_doc.get_password("api_secret")
		except Exception:
			api_secret = None

	if not api_key or not api_secret:
		api_key = frappe.generate_hash(length=15)
		api_secret = frappe.generate_hash(length=15)
		frappe.db.set_value("User", user, "api_key", api_key, update_modified=False)
		user_doc.set_password("api_secret", api_secret)
		frappe.db.commit()

	return api_key, api_secret


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
	api_key, api_secret = _get_or_generate_api_keys(user)

	return {
		"user": user,
		"full_name": user_doc.full_name or user,
		"api_key": api_key,
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
	api_key, api_secret = _get_or_generate_api_keys(user)

	return {
		"user": user,
		"full_name": user_doc.full_name or user,
		"api_key": api_key,
		"api_secret": api_secret,
	}
