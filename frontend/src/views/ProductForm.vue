<script setup lang="ts">
import { computed, ref } from "vue";
import { storage } from "../firebase";
import { ref as sRef, uploadBytes, getDownloadURL } from "firebase/storage";

type Form = {
  id_product_type?: number | null;
  id_unit_measurement?: number | null;
  code?: number | null;
  cname: string;
  description?: string | null;
  photo?: string | null;        // URL de imagen (lo llenamos al subir)
  unit_cost?: number | null;
  add_user?: number | null;
  add_date?: string | null;     // ISO string
  mod_user?: number | null;
  mod_date?: string | null;
};

// v-model (obligatorio)
const model = defineModel<Form>({ required: true });

const props = defineProps<{
  saving?: boolean;
  mode: "create" | "edit";
}>();

const emit = defineEmits<{
  (e: "save"): void;
  (e: "cancel"): void;
}>();

const title = computed(() =>
  props.mode === "edit" ? "Editar producto" : "Nuevo producto"
);

// ---------- Subida a Firebase ----------
const uploading = ref(false);
const uploadError = ref<string | null>(null);
const uploadPct = ref<number | null>(null);

async function onPickFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;

  // Validar tipo
  if (!file.type.startsWith("image/")) {
    uploadError.value = "Selecciona un archivo de imagen válido.";
    return;
  }

  // Generar ruta: products/<timestamp>_<rand>.<ext>
  const ext = file.name.includes(".")
    ? file.name.split(".").pop()
    : "jpg";
  const key = `products/${Date.now()}_${Math.random()
    .toString(36)
    .slice(2)}.${ext}`;

  try {
    uploadError.value = null;
    uploading.value = true;
    uploadPct.value = null;

    const refInStorage = sRef(storage, key);

    // Subimos el archivo
    const snap = await uploadBytes(refInStorage, file);
    // Obtenemos URL pública
    const url = await getDownloadURL(snap.ref);

    // Guardamos en el formulario (para enviar al backend)
    model.value.photo = url;
  } catch (err: any) {
    uploadError.value =
      err?.message || "No se pudo subir la imagen. Intenta de nuevo.";
  } finally {
    uploading.value = false;
    uploadPct.value = null;
    (e.target as HTMLInputElement).value = ""; // limpiar input
  }
}

// Formateo simple y tolerante
function fmtDate(v?: string | null) {
  if (!v) return "—";
  const d = new Date(v);
  if (!isNaN(d.getTime())) {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(
      d.getHours()
    )}:${pad(d.getMinutes())}`;
  }
  return v;
}
</script>

<template>
  <section class="space-y-4">
    <h2 class="text-xl font-semibold">{{ title }}</h2>

    <form @submit.prevent="emit('save')" class="space-y-4">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <!-- Imagen / preview -->
        <div class="md:col-span-1">
          <div class="space-y-3">
            <div class="flex items-center justify-center rounded-xl border bg-white p-2">
              <div class="h-36 w-36 overflow-hidden rounded-lg border bg-gray-50" title="Vista previa">
                <img
                  v-if="model.photo"
                  :src="model.photo"
                  alt="preview"
                  class="h-full w-full object-cover"
                  @error="(e:any)=>{ e.target.src=''; }"
                />
                <div
                  v-else
                  class="flex h-full w-full items-center justify-center text-xs text-gray-400"
                >
                  Sin imagen
                </div>
              </div>
            </div>

            <!-- Botón de subida -->
            <div class="flex items-center gap-3">
              <input
                id="fileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onPickFile"
              />
              <label
                for="fileInput"
                class="cursor-pointer rounded-lg border px-3 py-2 hover:bg-gray-50"
              >
                Subir imagen
              </label>

              <span v-if="uploading" class="text-sm text-gray-600">Subiendo…</span>
            </div>

            <p v-if="uploadError" class="text-sm text-red-600">
              {{ uploadError }}
            </p>
          </div>
        </div>

        <!-- Campos -->
        <div class="md:col-span-2 space-y-4">
          <label class="block space-y-1">
            <span class="text-sm">Nombre</span>
            <input
              v-model="model.cname"
              required
              class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label class="block space-y-1">
              <span class="text-sm">Código (número)</span>
              <input
                v-model.number="model.code"
                type="number"
                class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>

            <label class="block space-y-1">
              <span class="text-sm">Costo unitario</span>
              <input
                v-model.number="model.unit_cost"
                type="number"
                step="0.01"
                class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
          </div>

          <label class="block space-y-1">
            <span class="text-sm">Descripción</span>
            <textarea
              v-model="model.description"
              rows="4"
              class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
        </div>
      </div>

      <!-- Botones -->
      <div class="flex gap-2">
        <button
          :disabled="saving || uploading"
          class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ saving ? "Guardando…" : "Guardar" }}
        </button>
        <button
          type="button"
          @click="emit('cancel')"
          class="rounded-lg border px-4 py-2 hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>

      <!-- Metadatos -->
      <div class="mt-2 space-y-1 text-sm text-gray-600">
        <div>
          <span class="font-medium">Creado el:</span>
          <span class="ml-1 inline-flex items-center gap-2">
            <span class="rounded bg-gray-100 px-2 py-0.5">Usuario: {{ model.add_user ?? "—" }}</span>
            <span class="rounded bg-gray-100 px-2 py-0.5">Fecha: {{ fmtDate(model.add_date) }}</span>
          </span>
        </div>
        <div>
          <span class="font-medium">Modificado el:</span>
          <span class="ml-1 inline-flex items-center gap-2">
            <span class="rounded bg-gray-100 px-2 py-0.5">Usuario: {{ model.mod_user ?? "—" }}</span>
            <span class="rounded bg-gray-100 px-2 py-0.5">Fecha: {{ fmtDate(model.mod_date) }}</span>
          </span>
        </div>
      </div>
    </form>
  </section>
</template>
