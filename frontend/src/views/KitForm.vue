<script setup lang="ts">
import { computed } from "vue";
import KitsCompositionForm from "./KitsCompositionForm.vue";

type Form = {
  id_kit?: number;
  code?: number | null;
  cname: string;
  description?: string | null;
  photo?: string | null;

  // metadatos
  add_user?: number | null;
  add_date?: string | null;
  mod_user?: number | null;
  mod_date?: string | null;
};

// v-model del padre (KitsList.vue)
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
  props.mode === "edit" ? "Editar kit" : "Nuevo kit"
);

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
  <section class="space-y-6">
    <h2 class="text-xl font-semibold">{{ title }}</h2>

    <form @submit.prevent="emit('save')" class="space-y-4">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <!-- Imagen -->
        <div class="md:col-span-1">
          <div class="space-y-2">
            <div class="flex items-center justify-center rounded-xl border bg-white p-2">
              <div class="h-36 w-36 overflow-hidden rounded-lg border bg-gray-50">
                <img
                  v-if="model.photo"
                  :src="model.photo"
                  alt="preview"
                  class="h-full w-full object-cover"
                  @error="(e:any)=>{ e.target.src=''; }"
                />
                <div v-else class="flex h-full w-full items-center justify-center text-xs text-gray-400">
                  Sin imagen
                </div>
              </div>
            </div>

            <label class="block space-y-1">
              <span class="text-sm">Foto (URL)</span>
              <input
                v-model="model.photo"
                placeholder="https://…"
                class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
          </div>
        </div>

        <!-- Campos -->
        <div class="md:col-span-2 space-y-4">
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
              <span class="text-sm">Nombre</span>
              <input
                v-model="model.cname"
                required
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
          :disabled="props.saving"
          class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ props.saving ? "Guardando…" : "Guardar" }}
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

    <!-- Conformación del kit -->
    <div class="pt-2 border-t" v-if="model.id_kit">
      <h3 class="mb-2 text-lg font-semibold">Composición del kit</h3>
      <KitsCompositionForm :kit-id="model.id_kit!" />
    </div>

    <div v-else class="rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
      Guarda el kit para poder agregar los productos que lo conforman.
    </div>
  </section>
</template>
