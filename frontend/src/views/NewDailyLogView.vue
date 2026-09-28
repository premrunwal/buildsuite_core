<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import DeskPage from "@/components/desk/DeskPage.vue";
import DeskForm from "@/components/desk/DeskForm.vue";
import DeskSection from "@/components/desk/DeskSection.vue";
import DeskField from "@/components/desk/DeskField.vue";
import DeskInput from "@/components/desk/DeskInput.vue";
import DeskSelect from "@/components/desk/DeskSelect.vue";
import DeskTextarea from "@/components/desk/DeskTextarea.vue";
import { createDailyLog } from "@/data/dailyLogApi";
import { useDataStore } from "@/stores";
import { showToast } from "@/utils/appToast";
import { isCapacitor, takePhoto } from "@/utils/mobile";
import MobileFileUploadHandler from "@/utils/mobileFileUploadHandler";

const router = useRouter();
const store = useDataStore();

const form = ref({
	project: store.projects[0]?.name || "",
	entry_date: new Date().toISOString().slice(0, 10),
	weather_condition: "Clear",
	progress_percentage: 0,
	narrative: "",
	blocker_flag: false,
	blocker_details: "",
});

const saving = ref(false);
const pendingPhotos = ref([]);
const fileInput = ref(null);

const projects = computed(() =>
	(store.projects || []).map((p) => ({ value: p.name, label: p.project_name || p.name }))
);

const weatherOptions = [
	{ value: "Clear", label: "☀️ Clear / Sunny" },
	{ value: "Rainy", label: "🌧️ Rainy" },
	{ value: "Hot", label: "🌡️ High Heat" },
	{ value: "Cold", label: "❄️ Cold" },
	{ value: "Storm", label: "⛈️ Storm / Wind" },
];

async function captureSitePhoto() {
	if (isCapacitor()) {
		try {
			const photo = await takePhoto();
			if (photo && photo.webPath) {
				const response = await fetch(photo.webPath);
				const blob = await response.blob();
				const file = new File([blob], `log-photo-${Date.now()}.${photo.format || 'jpg'}`, { type: `image/${photo.format || 'jpeg'}` });
				pendingPhotos.value.push({
					file,
					previewUrl: URL.createObjectURL(file),
				});
			}
		} catch (e) {
			if (!e?.message?.includes("User cancelled")) {
				showToast(e.message || "Failed to capture photo", "danger");
			}
		}
	} else {
		fileInput.value?.click();
	}
}

function onFilesPicked(e) {
	const files = Array.from(e.target.files || []);
	files.forEach((file) => {
		pendingPhotos.value.push({
			file,
			previewUrl: URL.createObjectURL(file),
		});
	});
	e.target.value = "";
}

function removePendingPhoto(index) {
	pendingPhotos.value.splice(index, 1);
}

async function handleSubmit() {
	if (!form.value.project) {
		showToast("Please select a project", "danger");
		return;
	}

	saving.value = true;
	try {
		const docname = await createDailyLog({
			project: form.value.project,
			entry_date: form.value.entry_date,
			weather_condition: form.value.weather_condition,
			narrative: form.value.narrative,
			progress_percentage: form.value.progress_percentage,
			blocker_flag: form.value.blocker_flag ? 1 : 0,
			blocker_details: form.value.blocker_details,
		});

		// Upload any attached photos against this log
		if (pendingPhotos.value.length && docname) {
			const handler = new MobileFileUploadHandler();
			for (const p of pendingPhotos.value) {
				try {
					await handler.upload(p.file, {
						doctype: "Task Progress Entry",
						docname: docname,
						private: false,
					});
				} catch (err) {
					console.warn("Failed photo upload:", err);
				}
			}
		}

		showToast("Daily log submitted successfully!", "success");
		router.push("/daily-logs");
	} catch (e) {
		showToast(e.message || "Failed to save daily log", "danger");
	} finally {
		saving.value = false;
	}
}
</script>

<template>
	<DeskPage title="File Daily Log" subtitle="Record daily site execution progress, weather, and photos">
		<DeskForm @submit.prevent="handleSubmit">
			<DeskSection title="Site & Date Details" :cols="3">
				<DeskField label="Project" required>
					<DeskSelect v-model="form.project" :options="projects" required />
				</DeskField>

				<DeskField label="Log Date" required>
					<DeskInput v-model="form.entry_date" type="date" required />
				</DeskField>

				<DeskField label="Weather Condition">
					<DeskSelect v-model="form.weather_condition" :options="weatherOptions" />
				</DeskField>
			</DeskSection>

			<DeskSection title="Progress & Work Narrative" :cols="2">
				<DeskField label="Estimated Daily Progress (%)">
					<DeskInput v-model.number="form.progress_percentage" type="number" min="0" max="100" />
				</DeskField>

				<DeskField label="Blocker / Issue Alert">
					<div class="flex items-center gap-2 pt-2">
						<input
							id="blocker_check"
							v-model="form.blocker_flag"
							type="checkbox"
							class="w-4 h-4 text-brand-600 rounded border-ink-300 focus:ring-brand-500 cursor-pointer"
						/>
						<label for="blocker_check" class="text-xs font-semibold text-ink-900 cursor-pointer">
							Report a Site Blocker / Delay Issue
						</label>
					</div>
				</DeskField>

				<div class="col-span-2">
					<DeskField label="Daily Execution Summary & Narrative" required>
						<DeskTextarea
							v-model="form.narrative"
							rows="4"
							placeholder="Detail work done today, materials placed, teams active, and milestones reached..."
							required
						/>
					</DeskField>
				</div>

				<div v-if="form.blocker_flag" class="col-span-2">
					<DeskField label="Blocker Details & Required Resolution">
						<DeskTextarea
							v-model="form.blocker_details"
							rows="2"
							placeholder="Describe what is blocking site execution (e.g. material delay, drawing approval, weather stop)..."
						/>
					</DeskField>
				</div>
			</DeskSection>

			<DeskSection title="Attach Site Photos" :cols="1">
				<div class="flex flex-wrap items-center gap-3 mb-4">
					<button
						type="button"
						class="inline-flex items-center gap-2 px-3 py-2 bg-ink-900 hover:bg-ink-800 text-white text-xs font-medium rounded-lg cursor-pointer transition-colors"
						@click="captureSitePhoto"
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
							<circle cx="12" cy="13" r="4" stroke-width="2" />
						</svg>
						<span>Add Site Photo</span>
					</button>
					<input ref="fileInput" type="file" accept="image/*" capture="environment" multiple class="hidden" @change="onFilesPicked" />
					<span class="text-xs text-ink-400">Photos will be attached directly to this log</span>
				</div>

				<div v-if="pendingPhotos.length" class="flex flex-wrap gap-3">
					<div
						v-for="(p, index) in pendingPhotos"
						:key="index"
						class="relative w-20 h-20 rounded-lg overflow-hidden border border-ink-200 group"
					>
						<img :src="p.previewUrl" class="w-full h-full object-cover" />
						<button
							type="button"
							class="absolute top-1 right-1 w-5 h-5 bg-ink-900/80 text-white rounded-full text-xs flex items-center justify-center hover:bg-danger-600 transition-colors"
							@click="removePendingPhoto(index)"
						>
							✕
						</button>
					</div>
				</div>
			</DeskSection>

			<div class="mt-6 flex items-center gap-3 pt-4 border-t border-ink-200">
				<button
					type="submit"
					class="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 active:scale-98 text-white text-xs font-semibold rounded-lg shadow-sm transition-all cursor-pointer"
					:disabled="saving"
				>
					{{ saving ? "Saving Log..." : "Submit Daily Log" }}
				</button>
				<button
					type="button"
					class="px-4 py-2.5 bg-ink-100 hover:bg-ink-200 text-ink-700 text-xs font-medium rounded-lg transition-colors cursor-pointer"
					@click="router.back()"
				>
					Cancel
				</button>
			</div>
		</DeskForm>
	</DeskPage>
</template>
