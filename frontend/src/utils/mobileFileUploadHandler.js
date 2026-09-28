import OriginalFileUploadHandler from "../../node_modules/frappe-ui/src/utils/fileUploadHandler.ts";
import { resolveApiUrl, getStoredAuth, getServerUrl } from "./mobile";

class MobileFileUploadHandler extends OriginalFileUploadHandler {
	upload(file, options = {}) {
		const modifiedOptions = { ...options };
		const endpoint = modifiedOptions.upload_endpoint || "/api/method/upload_file";
		modifiedOptions.upload_endpoint = resolveApiUrl(endpoint);

		const auth = getStoredAuth();
		const serverUrl = getServerUrl();

		const originalUpload = super.upload.bind(this);

		// If on mobile or cross-origin with API keys, intercept XMLHttpRequest setup
		return new Promise((resolve, reject) => {
			const originalXhrOpen = XMLHttpRequest.prototype.open;
			const originalXhrSend = XMLHttpRequest.prototype.send;

			const restoreXhr = () => {
				XMLHttpRequest.prototype.open = originalXhrOpen;
				XMLHttpRequest.prototype.send = originalXhrSend;
			};

			XMLHttpRequest.prototype.open = function (method, url, ...args) {
				const res = originalXhrOpen.call(this, method, url, ...args);
				if (auth.hasToken) {
					this.setRequestHeader("Authorization", `token ${auth.apiKey}:${auth.apiSecret}`);
				}
				if (serverUrl) {
					try {
						const host = new URL(serverUrl).hostname;
						this.setRequestHeader("X-Frappe-Site-Name", host);
					} catch {
						// ignore
					}
				}
				this.withCredentials = true;
				return res;
			};

			originalUpload(file, modifiedOptions)
				.then((result) => {
					restoreXhr();
					resolve(result);
				})
				.catch((err) => {
					restoreXhr();
					reject(err);
				});
		});
	}
}

export default MobileFileUploadHandler;
