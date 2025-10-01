<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import api from "../api";
import KitForm from "./KitForm.vue";

type Kit = {
  id_kit: number;
  code?: number | null;
  cname: string;
  description?: string | null;
  photo?: string | null;
  add_user?: number | null;
  add_date?: string | null;
  mod_user?: number | null;
  mod_date?: string | null;
};

const rows = ref<Kit[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const q = ref("");
const showModal = ref(false);
const saving = ref(false);
const form = ref<Kit>({
  id_kit: 0,
  code: null,
  cname: "",
  description: "",
  photo: "",
});

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get<Kit[]>("/kits", {
      params: { q: q.value || undefined, limit: 50, skip: 0 },
    });
    rows.value = data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    loading.value = false;
  }
}

function openNew() {
  form.value = { id_kit: 0, code: null, cname: "", description: "", photo: "" };
  showModal.value = true;
}

function openEdit(k: Kit) {
  form.value = { ...k };
  showModal.value = true;
}

async function removeRow(id: number) {
  if (!confirm("¿Eliminar kit?")) return;
  try {
    await api.delete(`/kits/${id}`);
    await load();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  }
}

async function save() {
  saving.value = true;
  error.value = null;
  try {
    if (form.value.id_kit) {
      await api.put(`/kits/${form.value.id_kit}`, {
        code: form.value.code ?? null,
        cname: form.value.cname,
        description: form.value.description ?? null,
        photo: form.value.photo ?? null,
        mod_user: 1,
      });
    } else {
      await api.post("/kits", {
        code: form.value.code ?? null,
        cname: form.value.cname,
        description: form.value.description ?? null,
        photo: form.value.photo ?? null,
        add_user: 1,
      });
    }
    showModal.value = false;
    await load();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    saving.value = false;
  }
}

let t: number | undefined;
watch(q, () => {
  window.clearTimeout(t);
  t = window.setTimeout(load, 350);
});

onMounted(load);
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Kits</h2>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" @click="openNew">
        Nuevo
      </button>
    </div>

    <input
      v-model="q"
      placeholder="Buscar por nombre…"
      class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
    />

    <div v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ error }}
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">ID</th>
            <th class="px-3 py-2">Código</th>
            <th class="px-3 py-2">Nombre</th>
            <th class="px-3 py-2">Descripción</th>
            <th class="px-3 py-2">Foto</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="px-3 py-6 text-center text-gray-500">Cargando…</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="6" class="px-3 py-6 text-center text-gray-500">Sin resultados</td>
          </tr>
          <tr v-for="r in rows" :key="r.id_kit" class="border-t">
            <td class="px-3 py-2">{{ r.id_kit }}</td>
            <td class="px-3 py-2">{{ r.code ?? "—" }}</td>
            <td class="px-3 py-2">{{ r.cname }}</td>
            <td class="px-3 py-2">{{ r.description ?? "—" }}</td>
            <td class="px-3 py-2">
              <img v-if="r.photo" :src="r.photo" alt="" class="h-10 w-10 rounded object-cover" />
            </td>
            <td class="px-3 py-2 space-x-2 text-right">
              <button class="rounded border px-3 py-1 hover:bg-gray-50" @click="openEdit(r)">Editar</button>
              <button class="rounded border border-red-300 px-3 py-1 text-red-600 hover:bg-red-50" @click="removeRow(r.id_kit)">
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="mx-4 w-full max-w-3xl rounded-2xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-semibold">
          {{ form.id_kit ? "Editar kit" : "Nuevo kit" }}
        </h3>
        <KitForm v-model="form" :saving="saving" :mode="form.id_kit ? 'edit' : 'create'"
                 @save="save" @cancel="showModal = false" />
      </div>
    </div>
  </section>
</template>
