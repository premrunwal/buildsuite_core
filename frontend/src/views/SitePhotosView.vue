<script setup>
import { ref, onMounted, computed } from "vue";
import DeskPage from "@/components/desk/DeskPage.vue";
import DeskSection from "@/components/desk/DeskSection.vue";
import DeskSelect from "@/components/desk/DeskSelect.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { getSitePhotos } from "@/data/dailyLogApi";
import { useDataStore } from "@/stores";
import { showToast } from "@/utils/appToast";
import { isCapacitor, takePhoto } from "@/utils/mobile";
import MobileFileUploadHandler from "@/utils/mobileFileUploadHandler";

const store = useDataStore();
const photos = ref([]);
const loading = ref(true);
const selectedProject = ref("");
const uploading = ref(false);
const photoInput = ref(null);
const activePhoto = ref(null);

const projects = computed(() => {
	const list = store.projects || [];
	return [
		{ value: "", label: "All Projects" },
		...list.map((p) => ({ value: p.name, label: p.project_name || p.name })),
	];
});

async function fetchPhotos() {
	loading.value = true;
	try {
		photos.value = await getSitePhotos({ project: selectedProject.value || undefined });
	} catch (e) {
		console.error("Failed to load site photos", e);
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	fetchPhotos();
});

async function triggerCameraUpload() {
	if (isCapacitor()) {
		try {
			const photo = await takePhoto();
			if (photo && photo.webPath) {
				const response = await fetch(photo.webPath);
				const blob = await response.blob();
				const file = new File([blob], `site-photo-${Date.now()}.${photo.format || 'jpg'}`, { type: `image/${photo.format || 'jpeg'}` });
				await processFileUpload(file);
			}
		} catch (e) {
			if (!e?.message?.includes("User cancelled")) {
				showToast(e.message || "Failed to capture photo", "danger");
			}
		}
	} else {
		photoInput.value?.click();
	}
}

async function onFileSelected(e) {
	const files = Array.from(e.target.files || []);
	if (!files.length) return;
	for (const file of files) {
		await processFileUpload(file);
	}
	e.target.value = "";
}

async function processFileUpload(file) {
	uploading.value = true;
	try {
		const handler = new MobileFileUploadHandler();
		const result = await handler.upload(file, {
			doctype: "Project",
			docname: selectedProject.value || (store.projects[0]?.name || "Site-Photo"),
			private: false,
		});
		showToast("Photo uploaded successfully!", "success");
		await fetchPhotos();
	} catch (err) {
		showToast(err.message || "Upload failed", "danger");
	} finally {
		uploading.value = false;
	}
}

function openLightbox(photo) {
	activePhoto.value = photo;
}
function closeLightbox() {
	activePhoto.value = null;
}
</script>

<template>
	<DeskPage title="Site Photos" subtitle="Capture & inspect real-time construction site progress photographs">
		<template #actions>
			<button
				type="button"
				class="inline-flex items-center gap-2 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 active:scale-98 text-white text-xs font-semibold rounded-lg shadow-sm transition-all cursor-pointer"
				:disabled="uploading"
				@click="triggerCameraUpload"
			>
				<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					<circle cx="12" cy="13" r="4" stroke-width="2" />
				</svg>
				<span>{{ uploading ? "Uploading..." : "Take Photo" }}</span>
			</button>
			<input
				ref="photoInput"
				type="file"
				accept="image/*"
				capture="environment"
				multiple
				class="hidden"
				@change="onFileSelected"
			/>
		</template>

		<!-- Filters bar -->
		<div class="mb-6 flex flex-wrap items-center justify-between gap-4 bg-white p-4 border border-ink-200 rounded-xl shadow-xs">
			<div class="w-full sm:w-64">
				<label class="block text-[11px] uppercase tracking-wider font-semibold text-ink-500 mb-1">Project Filter</label>
				<DeskSelect
					v-model="selectedProject"
					:options="projects"
					@change="fetchPhotos"
				/>
			</div>
			<div class="text-xs text-ink-500 font-medium">
				Showing <span class="font-bold text-ink-900">{{ photos.length }}</span> site photo{{ photos.length === 1 ? '' : 's' }}
			</div>
		</div>

		<!-- Skeleton Loader -->
		<div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
			<div v-for="n in 8" :key="n" class="animate-pulse bg-ink-100 rounded-xl aspect-square"></div>
		</div>

		<!-- Photos Grid -->
		<div v-else-if="photos.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
			<div
				v-for="photo in photos"
				:key="photo.name"
				class="group bg-white border border-ink-200 rounded-xl overflow-hidden shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer flex flex-col"
				@click="openLightbox(photo)"
			>
				<div class="relative aspect-4/3 bg-ink-900 overflow-hidden">
					<img
						:src="photo.file_url"
						:alt="photo.file_name"
						class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
						loading="lazy"
					/>
					<div class="absolute inset-0 bg-gradient-to-t from-ink-950/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
						<span class="text-xs font-medium text-white flex items-center gap-1.5">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
							</svg>
							View Full Photo
						</span>
					</div>
				</div>
				<div class="p-3 flex flex-col flex-1 justify-between bg-white">
					<div class="text-xs font-semibold text-ink-900 truncate mb-1" :title="photo.file_name">
						{{ photo.file_name }}
					</div>
					<div class="flex items-center justify-between text-[11px] text-ink-500 mt-2 pt-2 border-t border-ink-100">
						<span class="truncate">{{ photo.uploader || "Site Engineer" }}</span>
						<span class="shrink-0 font-mono">{{ new Date(photo.creation).toLocaleDateString() }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Empty State -->
		<div v-else class="bg-white border border-ink-200 rounded-xl p-12 text-center my-6 max-w-md mx-auto">
			<div class="w-16 h-16 rounded-full bg-brand-50 text-brand-600 mx-auto flex items-center justify-center mb-4">
				<svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
					<circle cx="12" cy="13" r="4" stroke-width="1.5" />
				</svg>
			</div>
			<h3 class="text-base font-semibold text-ink-900 mb-1">No site photos uploaded yet</h3>
			<p class="text-xs text-ink-500 mb-5">Tap below to capture your first site photo directly from your device camera.</p>
			<button
				type="button"
				class="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-sm"
				@click="triggerCameraUpload"
			>
				Capture Photo
			</button>
		</div>

		<!-- Lightbox Modal -->
		<div
			v-if="activePhoto"
			class="fixed inset-0 z-50 bg-ink-950/90 backdrop-blur-sm flex items-center justify-center p-4"
			@click="closeLightbox"
		>
			<div class="relative max-w-4xl w-full bg-ink-900 rounded-2xl overflow-hidden shadow-2xl border border-ink-700" @click.stop>
				<button
					type="button"
					class="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-ink-800/80 hover:bg-ink-700 text-white flex items-center justify-center transition-colors"
					@click="closeLightbox"
				>
					✕
				</button>
				<div class="max-h-[75vh] flex items-center justify-center bg-black">
					<img
						:src="activePhoto.file_url"
						:alt="activePhoto.file_name"
						class="max-h-[75vh] w-auto object-contain"
					/>
				</div>
				<div class="p-5 bg-ink-900 text-white flex items-center justify-between">
					<div>
						<h4 class="text-sm font-semibold">{{ activePhoto.file_name }}</h4>
						<p class="text-xs text-ink-400 mt-0.5">Uploaded by {{ activePhoto.uploader }} · {{ new Date(activePhoto.creation).toLocaleString() }}</p>
					</div>
					<a
						:href="activePhoto.file_url"
						target="_blank"
						download
						class="px-3 py-1.5 bg-ink-800 hover:bg-ink-700 text-xs font-medium rounded-lg text-ink-200 transition-colors"
					>
						Download
					</a>
				</div>
			</div>
		</div>
	</DeskPage>
</template>
