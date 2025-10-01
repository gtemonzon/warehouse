<!-- frontend/src/views/WarehouseForm.vue -->
<script setup lang="ts">
import { computed } from "vue";

type Form = {
  id_warehouse?: number;
  code?: number | null;
  cname: string;
  description?: string | null;
  add_user?: number | null;
  add_date?: string | null;
  mod_user?: number | null;
  mod_date?: string | null;
};

const model = defineModel<Form>({ required: true });

const props = defineProps<{
  saving?: boolean;
  mode: "create" | "edit";
}>();

const emit = defineEmits<{
  (e: "save"): void;
  (e: "cancel"): void;
}>();

const title = computed(() => (props.mode === "edit" ? "Editar almacén" : "Nuevo almacén"));

function fmtDate(v?: string | null) {
  if (!v) return "—";
  const d = new Date(v);
  if (!isNaN(d.getTime())) {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }
  return v;
}
</script>

<template>
  <form @submit.prevent="emit('save')" class="space-y-4">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <label class="block space-y-1">
        <span class="text-sm">Código (número)</span>
        <input v-model.number="model.code" type="number"
               class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
      </label>

      <label class="block space-y-1">
        <span class="text-sm">Nombre</span>
        <input v-model="model.cname" required
               class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
      </label>
    </div>

    <label class="block space-y-1">
      <span class="text-sm">Descripción</span>
      <textarea v-model="model.description" rows="4"
                class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
    </label>

    <div class="flex gap-2">
      <button :disabled="saving"
              class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50">
        {{ saving ? "Guardando…" : "Guardar" }}
      </button>
      <button type="button" @click="emit('cancel')" class="rounded-lg border px-4 py-2 hover:bg-gray-50">
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
</template>
