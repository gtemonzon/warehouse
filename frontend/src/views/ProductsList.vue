<script setup lang="ts">
import { onMounted, ref, watch, nextTick, computed } from "vue";
import api from "../api";
import ProductForm from "./ProductForm.vue";

type Product = {
  id_product: number;
  code?: number | null;
  cname: string;
  unit_cost?: number | null;
  photo?: string | null;
  description?: string | null;
  id_product_type?: number | null;
  id_unit_measurement?: number | null;
  add_user?: number | null;
  add_date?: string | null;
  mod_user?: number | null;
  mod_date?: string | null;
};

type Inventory = {
  id_product: number;
  stock: number;
};

const loading = ref(false);
const q = ref("");
const rows = ref<Product[]>([]);
const inventory = ref<Map<number, number>>(new Map());
const error = ref<string | null>(null);

// Modal state
const showModal = ref(false);
const mode = ref<"create" | "edit">("create");
const saving = ref(false);
const editingId = ref<number | null>(null);
const form = ref<Product>({
  id_product: 0,
  code: null,
  cname: "",
  unit_cost: null,
  photo: "",
  description: "",
});

// Obtener stock de un producto
function getStock(productId: number): number {
  return inventory.value.get(productId) || 0;
}

// Cargar inventario
async function loadInventory() {
  try {
    const { data } = await api.get<Inventory[]>("/products/inventory/summary");
    const map = new Map<number, number>();
    data.forEach(item => map.set(item.id_product, item.stock));
    inventory.value = map;
  } catch (e: any) {
    console.error("Error cargando inventario:", e);
  }
}

// Cargar productos
async function load() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get<Product[]>("/products", {
      params: { q: q.value || undefined, limit: 200, skip: 0 },
    });
    rows.value = data;
    await loadInventory();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    loading.value = false;
  }
}

async function removeRow(id: number) {
  if (!confirm("¿Eliminar producto?")) return;
  try {
    await api.delete(`/products/${id}`);
    await load();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  }
}

// Modal helpers
function openCreate() {
  mode.value = "create";
  editingId.value = null;
  form.value = {
    id_product: 0,
    code: null,
    cname: "",
    unit_cost: null,
    photo: "",
    description: "",
  };
  showModal.value = true;
}

async function openEdit(id: number) {
  try {
    mode.value = "edit";
    editingId.value = id;
    error.value = null;
    saving.value = false;
    const { data } = await api.get<Product>(`/products/${id}`);
    form.value = {
      ...form.value,
      ...data,
    };
    showModal.value = true;
    await nextTick();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  }
}

function closeModal() {
  showModal.value = false;
}

// Guardar (create/update)
async function submitForm() {
  try {
    saving.value = true;
    error.value = null;
    if (mode.value === "edit" && editingId.value) {
      await api.put(`/products/${editingId.value}`, {
        id_product_type: form.value.id_product_type ?? null,
        id_unit_measurement: form.value.id_unit_measurement ?? null,
        code:
          form.value.code === undefined || form.value.code === null
            ? null
            : Number(form.value.code),
        cname: form.value.cname,
        description: form.value.description ?? null,
        photo: form.value.photo ?? null,
        unit_cost:
          form.value.unit_cost === undefined || form.value.unit_cost === null
            ? null
            : Number(form.value.unit_cost),
        mod_user: 1,
      });
    } else {
      await api.post("/products", {
        id_product_type: form.value.id_product_type ?? null,
        id_unit_measurement: form.value.id_unit_measurement ?? null,
        code:
          form.value.code === undefined || form.value.code === null
            ? null
            : Number(form.value.code),
        cname: form.value.cname,
        description: form.value.description ?? null,
        photo: form.value.photo ?? null,
        unit_cost:
          form.value.unit_cost === undefined || form.value.unit_cost === null
            ? null
            : Number(form.value.unit_cost),
        add_user: 1,
      });
    }
    closeModal();
    await load();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    saving.value = false;
  }
}

// Live search (debounce)
let t: any;
watch(
  q,
  () => {
    clearTimeout(t);
    t = setTimeout(load, 350);
  },
  { immediate: false }
);

onMounted(load);
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Productos</h2>
      <button
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        @click="openCreate"
      >
        Nuevo
      </button>
    </div>

    <div class="flex items-center gap-2">
      <input
        v-model="q"
        placeholder="Buscar por nombre…"
        class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button @click="load" class="rounded-lg border px-4 py-2 hover:bg-gray-50">
        Buscar
      </button>
    </div>

    <div
      v-if="error"
      class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">ID</th>
            <th class="px-3 py-2">Código</th>
            <th class="px-3 py-2">Nombre</th>
            <th class="px-3 py-2">Costo</th>
            <th class="px-3 py-2 text-center">Existencias</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="px-3 py-6 text-center text-gray-500">
              Cargando…
            </td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="6" class="px-3 py-6 text-center text-gray-500">
              Sin resultados
            </td>
          </tr>
          <tr v-for="r in rows" :key="r.id_product" class="border-t">
            <td class="px-3 py-2">{{ r.id_product }}</td>
            <td class="px-3 py-2">{{ r.code ?? "—" }}</td>
            <td class="px-3 py-2">{{ r.cname }}</td>
            <td class="px-3 py-2">{{ r.unit_cost ?? "—" }}</td>
            <td class="px-3 py-2 text-center">
              <span 
                :class="[
                  'inline-block rounded px-2 py-1 font-medium',
                  getStock(r.id_product) > 0 
                    ? 'bg-green-100 text-green-800' 
                    : getStock(r.id_product) === 0
                    ? 'bg-gray-100 text-gray-600'
                    : 'bg-red-100 text-red-800'
                ]"
              >
                {{ getStock(r.id_product) }}
              </span>
            </td>
            <td class="px-3 py-2 space-x-2 text-right">
              <button
                class="rounded border px-3 py-1 hover:bg-gray-50"
                @click="openEdit(r.id_product)"
              >
                Editar
              </button>
              <button
                class="rounded border border-red-300 px-3 py-1 text-red-600 hover:bg-red-50"
                @click="removeRow(r.id_product)"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <transition name="fade">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
        @keydown.esc="closeModal"
      >
        <div
          class="w-full max-w-2xl rounded-2xl bg-white p-6 shadow-xl"
          role="dialog"
          aria-modal="true"
        >
          <ProductForm
            v-model="form"
            :saving="saving"
            :mode="mode"
            @save="submitForm"
            @cancel="closeModal"
          />
        </div>
      </div>
    </transition>
  </section>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>