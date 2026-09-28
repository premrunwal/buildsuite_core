<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import LogoIcon from "@/components/LogoIcon.vue";
import { getServerUrl, setServerUrl, validateServerUrl } from "@/utils/mobile";

const router = useRouter();
const route = useRoute();

const serverUrlInput = ref("");
const isValidating = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

onMounted(() => {
	const current = getServerUrl();
	if (current) {
		serverUrlInput.value = current;
	} else if (import.meta.env.DEV) {
		serverUrlInput.value = "http://localhost:8000";
	}
});

async function handleConnect() {
	errorMessage.value = "";
	successMessage.value = "";

	let raw = serverUrlInput.value.trim();
	if (!raw) {
		errorMessage.value = "Please enter your Frappe/ERPNext server address.";
		return;
	}

	if (!raw.startsWith("http://") && !raw.startsWith("https://")) {
		raw = "https://" + raw;
		serverUrlInput.value = raw;
	}

	isValidating.value = true;
	try {
		await validateServerUrl(raw);
		await setServerUrl(raw);
		successMessage.value = "Server connected successfully!";
		setTimeout(() => {
			const redirect = route.query.redirect || "/login";
			router.push(redirect);
		}, 600);
	} catch (err) {
		errorMessage.value = err.message || "Could not reach server. Verify the URL and network.";
	} finally {
		isValidating.value = false;
	}
}
</script>

<template>
	<div class="min-h-screen bg-ink-950 text-white flex flex-col justify-center px-6 py-12">
		<div class="max-w-md w-full mx-auto space-y-8">
			<!-- Header -->
			<div class="text-center space-y-3">
				<div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/30 text-brand-400">
					<LogoIcon class="w-10 h-10" />
				</div>
				<h1 class="text-2xl font-bold tracking-tight text-ink-50">BuildSuite Mobile</h1>
				<p class="text-sm text-ink-400">Connect to your Frappe / ERPNext server to get started.</p>
			</div>

			<!-- Card -->
			<div class="bg-ink-900 border border-ink-800 rounded-2xl p-6 shadow-xl space-y-5">
				<div>
					<label class="block text-xs font-semibold uppercase tracking-wider text-ink-400 mb-2">
						Server Address
					</label>
					<div class="relative">
						<input
							v-model="serverUrlInput"
							type="url"
							placeholder="https://erp.example.com"
							class="w-full bg-ink-950 border border-ink-700 rounded-xl px-4 py-3.5 text-ink-100 placeholder-ink-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-base"
							@keydown.enter="handleConnect"
						/>
					</div>
					<p class="text-xs text-ink-500 mt-2">
						Enter the full URL of your ERPNext or Frappe instance (e.g. <span class="font-mono text-ink-400">https://erp.mycompany.com</span>).
					</p>
				</div>

				<!-- Alert messages -->
				<div v-if="errorMessage" class="p-3.5 rounded-xl bg-danger-500/10 border border-danger-500/30 text-danger-400 text-sm flex items-start gap-2.5">
					<svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
					<span>{{ errorMessage }}</span>
				</div>

				<div v-if="successMessage" class="p-3.5 rounded-xl bg-success-500/10 border border-success-500/30 text-success-400 text-sm flex items-center gap-2.5">
					<svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
					</svg>
					<span>{{ successMessage }}</span>
				</div>

				<!-- Action button -->
				<button
					type="button"
					:disabled="isValidating"
					class="w-full min-h-[48px] flex items-center justify-center font-medium rounded-xl bg-brand-500 hover:bg-brand-600 active:bg-brand-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-brand-500/20"
					@click="handleConnect"
				>
					<svg v-if="isValidating" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					<span>{{ isValidating ? "Connecting..." : "Connect Server" }}</span>
				</button>
			</div>

			<!-- Footer note -->
			<div class="text-center">
				<p class="text-xs text-ink-500">
					BuildSuite Core Mobile • Version 1.0.0
				</p>
			</div>
		</div>
	</div>
</template>
