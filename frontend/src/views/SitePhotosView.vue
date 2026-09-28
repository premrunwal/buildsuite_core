<script setup>
import { ref, onMounted, computed } from "vue";
import DeskPage from "@/components/desk/DeskPage.vue";
import DeskSelect from "@/components/desk/DeskSelect.vue";
import { getSitePhotos } from "@/data/dailyLogApi";
import { useDataStore } from "@/stores";
import { showToast } from "@/utils/appToast";
import { isCapacitor, takePhoto } from "@/utils/mobile";
import MobileFileUploadHandler from "@/utils/mobileFileUploadHandler";

const store = useDataStore();
const photos = ref([]);
const loading = ref(true);
const selectedProject = ref("");

const pendingPreviews = ref([]);
const uploading = ref(false);
const uploadProgress = ref({ current: 0, total: 0 });
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
				await processBatchFileUpload([file]);
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

function triggerGalleryMultiUpload() {
	photoInput.value?.click();
}

async function onFilesSelected(e) {
	const files = Array.from(e.target.files || []);
	if (!files.length) return;

	// Create instant direct local image previews
	pendingPreviews.value = files.map((file) => ({
		file,
		url: URL.createObjectURL(file),
		name: file.name,
		size: `${(file.size / 1024).toFixed(0)} KB`,
	}));

	await processBatchFileUpload(files);
	e.target.value = "";
}

async function processBatchFileUpload(files) {
	if (!files || !files.length) return;
	uploading.value = true;
	uploadProgress.value = { current: 0, total: files.length };

	const handler = new MobileFileUploadHandler();
	const targetProject = selectedProject.value || (store.projects[0]?.name || "Site-Photo");
	let successCount = 0;

	for (let i = 0; i < files.length; i++) {
		uploadProgress.value.current = i + 1;
		try {
			await handler.upload(files[i], {
				doctype: "Project",
				docname: targetProject,
				private: false,
			});
			successCount++;
		} catch (err) {
			console.warn("Photo upload failed:", files[i].name, err);
		}
	}

	uploading.value = false;
	pendingPreviews.value = [];
	showToast(`Successfully uploaded ${successCount} of ${files.length} photos!`, "success");
	await fetchPhotos();
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
			<div class="flex items-center gap-2">
				<button
					type="button"
					class="inline-flex items-center gap-2 px-3 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs transition-all cursor-pointer"
					:disabled="uploading"
					@click="triggerGalleryMultiUpload"
				>
					<svg class="w-4 h-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
					<span>Upload Multiple Photos</span>
				</button>

				<button
					type="button"
					class="inline-flex items-center gap-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-all cursor-pointer"
					:disabled="uploading"
					@click="triggerCameraUpload"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
						<circle cx="12" cy="13" r="4" stroke-width="2" />
					</svg>
					<span>Camera</span>
				</button>
			</div>

			<input
				ref="photoInput"
				type="file"
				accept="image/*"
				multiple
				class="hidden"
				@change="onFilesSelected"
			/>
		</template>

		<!-- Instant Direct Image Previews & Batch Progress Bar -->
		<div v-if="pendingPreviews.length" class="mb-6 bg-slate-900 border border-slate-800 rounded-2xl p-5 text-white shadow-md">
			<div class="flex items-center justify-between mb-3">
				<div class="flex items-center gap-2.5">
					<div class="w-3.5 h-3.5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
					<span class="text-xs font-bold uppercase tracking-wider text-slate-200">Instant Direct Photo Previews (Uploading {{ uploadProgress.current }} of {{ uploadProgress.total }})</span>
				</div>
				<span class="text-xs font-mono font-bold text-emerald-400">{{ Math.round((uploadProgress.current / uploadProgress.total) * 100) }}%</span>
			</div>

			<!-- Direct Thumbnails Grid -->
			<div class="flex items-center gap-3 overflow-x-auto pb-2 no-scrollbar">
				<div
					v-for="(item, idx) in pendingPreviews"
					:key="idx"
					class="relative w-20 h-20 rounded-xl overflow-hidden border border-slate-700 bg-slate-950 shrink-0 cursor-pointer group"
					@click="openLightbox({ file_url: item.url, file_name: item.name, uploader: 'Instant Preview' })"
				>
					<img :src="item.url" class="w-full h-full object-cover group-hover:scale-105 transition-transform" />
					<div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
						<span class="text-[10px] text-white font-bold">Preview</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Filters bar -->
		<div class="mb-6 flex flex-wrap items-center justify-between gap-4 bg-white p-4 border border-slate-200 rounded-xl shadow-xs">
			<div class="w-full sm:w-64">
				<label class="block text-[11px] uppercase tracking-wider font-bold text-slate-500 mb-1">Filter by Project</label>
				<DeskSelect
					v-model="selectedProject"
					:options="projects"
					@change="fetchPhotos"
				/>
			</div>
			<div class="text-xs text-slate-500 font-medium">
				Showing <span class="font-extrabold text-slate-900 font-mono">{{ photos.length }}</span> site photo{{ photos.length === 1 ? '' : 's' }}
			</div>
		</div>

		<!-- Skeleton Loader -->
		<div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
			<div v-for="n in 8" :key="n" class="animate-pulse bg-slate-100 rounded-xl aspect-square"></div>
		</div>

		<!-- Photos Grid -->
		<div v-else-if="photos.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
			<div
				v-for="photo in photos"
				:key="photo.name"
				class="group bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer flex flex-col"
				@click="openLightbox(photo)"
			>
				<div class="relative aspect-4/3 bg-slate-950 overflow-hidden">
					<img
						:src="photo.file_url"
						:alt="photo.file_name"
						class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
						loading="lazy"
					/>
					<div class="absolute inset-0 bg-gradient-to-t from-slate-950/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-3">
						<span class="text-xs font-semibold text-white flex items-center gap-1.5">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
							</svg>
							Direct Full Preview
						</span>
					</div>
				</div>
				<div class="p-3.5 flex flex-col flex-1 justify-between bg-white">
					<div class="text-xs font-bold text-slate-900 truncate mb-1" :title="photo.file_name">
						{{ photo.file_name }}
					</div>
					<div class="flex items-center justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-100">
						<span class="truncate font-medium">{{ photo.uploader || "Site Engineer" }}</span>
						<span class="shrink-0 font-mono text-slate-400">{{ new Date(photo.creation).toLocaleDateString() }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Empty State -->
		<div v-else class="bg-white border border-slate-200 rounded-2xl p-12 text-center my-6 max-w-md mx-auto shadow-xs">
			<div class="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 mx-auto flex items-center justify-center mb-4">
				<svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
				</svg>
			</div>
			<h3 class="text-base font-bold text-slate-900 mb-1">No site photos uploaded yet</h3>
			<p class="text-xs text-slate-500 mb-5">Select single or multiple photos from your gallery to upload them with direct image previews.</p>
			<button
				type="button"
				class="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-xs cursor-pointer"
				@click="triggerGalleryMultiUpload"
			>
				Upload Multiple Photos
			</button>
		</div>

		<!-- Direct Image Lightbox Modal -->
		<div
			v-if="activePhoto"
			class="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-sm flex items-center justify-center p-4"
			@click="closeLightbox"
		>
			<div class="relative max-w-4xl w-full bg-slate-900 rounded-2xl overflow-hidden shadow-2xl border border-slate-800" @click.stop>
				<button
					type="button"
					class="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-slate-800/80 hover:bg-slate-700 text-white flex items-center justify-center transition-colors cursor-pointer font-bold"
					@click="closeLightbox"
				>
					✕
				</button>
				<div class="max-h-[75vh] flex items-center justify-center bg-black p-2">
					<img
						:src="activePhoto.file_url"
						:alt="activePhoto.file_name"
						class="max-h-[75vh] w-auto object-contain rounded-lg"
					/>
				</div>
				<div class="p-5 bg-slate-900 text-white flex items-center justify-between">
					<div>
						<h4 class="text-sm font-bold text-white">{{ activePhoto.file_name }}</h4>
						<p class="text-xs text-slate-400 mt-0.5">Uploaded by {{ activePhoto.uploader }} · {{ activePhoto.creation ? new Date(activePhoto.creation).toLocaleString() : 'Just now' }}</p>
					</div>
					<a
						:href="activePhoto.file_url"
						target="_blank"
						download
						class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-xl text-slate-200 transition-colors"
					>
						Download Photo
					</a>
				</div>
			</div>
		</div>
	</DeskPage>
</template>
