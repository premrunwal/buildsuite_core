import frappe
from frappe import _


@frappe.whitelist(methods=["POST"])
def get_or_create_api_keys():
	"""Whitelisted endpoint for authenticated mobile app users to obtain API Key & Secret.

	Enforces that the user is logged in (not Guest) and has BuildSuite Core permission.
	Generates an API key and secret if none exist, or safely retrieves the secret.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	from buildsuite_core.api.permission import _has_app_permission

	if not _has_app_permission(log_denial=True):
		frappe.throw(
			_("User does not have permission to access BuildSuite Core"),
			frappe.PermissionError,
		)

	user_doc = frappe.get_doc("User", frappe.session.user)
	api_secret = None

	if not user_doc.api_key:
		user_doc.set_api_key()
		api_secret = user_doc.set_api_secret()
	else:
		try:
			api_secret = user_doc.get_password("api_secret")
		except Exception:
			api_secret = None

		if not api_secret:
			api_secret = user_doc.set_api_secret()

	return {
		"user": frappe.session.user,
		"api_key": user_doc.api_key,
		"api_secret": api_secret,
	}
