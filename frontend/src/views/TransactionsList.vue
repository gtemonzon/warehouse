<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import api from "../api";
import TransactionForm from "./TransactionForm.vue";

type Tx = {
  id_product_transaction: number;
  id_product: number | null;
  id_warehouse: number | null;
  type_transaction: number;
  id_planification_expense_request?: number | null;
  id_kit?: number | null;
  quantaty_kit?: number | null;
  quantaty_products: number | null;
  description?: string | null;
  expiration_date?: string | null;
  add_user?: number | null;
  add_date?: string | null;
  mod_user?: number | null;
  mod_date?: string | null;
  product_name?: string;
  warehouse_name?: string;
  kit_name?: string;
};

const rows = ref<Tx[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const q = ref("");
const filterType = ref<"all" | "entrada" | "salida">("all");
const showModal = ref(false);
const saving = ref(false);
const form = ref<Tx>({
  id_product_transaction: 0,
  id_product: null,
  id_warehouse: null,
  type_transaction: 0,
  quantaty_products: null,
  description: "",
  expiration_date: "",
  id_kit: null,
  quantaty_kit: null,
  id_planification_expense_request: null,
});

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const params: any = { q: q.value || undefined, limit: 100, skip: 0 };
    if (filterType.value === "entrada") params.type_transaction = 0;
    if (filterType.value === "salida") params.type_transaction = 1;
    
    const { data } = await api.get<Tx[]>("/transactions", { params });
    rows.value = data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    loading.value = false;
  }
}

function openNew() {
  form.value = {
    id_product_transaction: 0,
    id_product: null,
    id_warehouse: null,
    type_transaction: 0,
    quantaty_products: null,
    description: "",
    expiration_date: "",
    id_kit: null,
    quantaty_kit: null,
    id_planification_expense_request: null,
  };
  showModal.value = true;
}

function openEdit(tx: Tx) {
  form.value = { ...tx };
  showModal.value = true;
}

async function removeRow(id: number) {
  if (!confirm("¿Eliminar movimiento?")) return;
  try {
    await api.delete(`/transactions/${id}`);
    await load();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  }
}

async function save() {
  saving.value = true;
  error.value = null;
  try {
    if (form.value.id_product_transaction) {
      await api.put(`/transactions/${form.value.id_product_transaction}`, {
        id_product: form.value.id_product,
        id_warehouse: form.value.id_warehouse,
        type_transaction: form.value.type_transaction,
        id_planification_expense_request: form.value.id_planification_expense_request ?? null,
        id_kit: form.value.id_kit ?? null,
        quantaty_kit: form.value.quantaty_kit ?? null,
        quantaty_products: form.value.quantaty_products,
        description: form.value.description ?? null,
        expiration_date: form.value.expiration_date || null,
        mod_user: 1,
      });
    } else {
      await api.post("/transactions", {
        id_product: form.value.id_product,
        id_warehouse: form.value.id_warehouse,
        type_transaction: form.value.type_transaction,
        id_planification_expense_request: form.value.id_planification_expense_request ?? null,
        id_kit: form.value.id_kit ?? null,
        quantaty_kit: form.value.quantaty_kit ?? null,
        quantaty_products: form.value.quantaty_products,
        description: form.value.description ?? null,
        expiration_date: form.value.expiration_date || null,
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

function formatDate(dateStr?: string | null) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString();
}

let t: number | undefined;
watch(q, () => {
  window.clearTimeout(t);
  t = window.setTimeout(load, 350);
});

watch(filterType, () => {
  load();
});

onMounted(load);
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold">Movimientos de Inventario</h2>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" @click="openNew">
        Nuevo Movimiento
      </button>
    </div>

    <div class="flex items-center gap-3">
      <input
        v-model="q"
        placeholder="Buscar por descripción…"
        class="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
      />
      
      <select 
        v-model="filterType"
        class="rounded-lg border border-gray-300 bg-white px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="all">Todos</option>
        <option value="entrada">Entradas</option>
        <option value="salida">Salidas</option>
      </select>
    </div>

    <div v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ error }}
    </div>

    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">ID</th>
            <th class="px-3 py-2">Tipo</th>
            <th class="px-3 py-2">Producto</th>
            <th class="px-3 py-2">Almacén</th>
            <th class="px-3 py-2 text-center">Cantidad</th>
            <th class="px-3 py-2">Kit</th>
            <th class="px-3 py-2">F. Venc.</th>
            <th class="px-3 py-2">Descripción</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9" class="px-3 py-6 text-center text-gray-500">Cargando…</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="9" class="px-3 py-6 text-center text-gray-500">Sin resultados</td>
          </tr>
          <tr v-for="r in rows" :key="r.id_product_transaction" class="border-t hover:bg-gray-50">
            <td class="px-3 py-2 text-gray-600">{{ r.id_product_transaction }}</td>
            <td class="px-3 py-2">
              <span 
                :class="[
                  'inline-block rounded px-2 py-1 text-xs font-semibold',
                  r.type_transaction === 0 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                ]"
              >
                {{ r.type_transaction === 0 ? 'Entrada' : 'Salida' }}
              </span>
            </td>
            <td class="px-3 py-2 font-medium">{{ r.product_name || `#${r.id_product}` }}</td>
            <td class="px-3 py-2">{{ r.warehouse_name || `#${r.id_warehouse}` }}</td>
            <td class="px-3 py-2 text-center">
              <span class="font-semibold">{{ r.quantaty_products ?? '—' }}</span>
            </td>
            <td class="px-3 py-2 text-sm text-gray-600">
              {{ r.kit_name || (r.id_kit ? `#${r.id_kit}` : '—') }}
            </td>
            <td class="px-3 py-2 text-sm text-gray-600">{{ formatDate(r.expiration_date) }}</td>
            <td class="px-3 py-2 text-sm text-gray-600 max-w-xs truncate" :title="r.description || ''">
              {{ r.description || '—' }}
            </td>
            <td class="px-3 py-2 space-x-2 text-right">
              <button class="rounded border px-3 py-1 hover:bg-gray-50" @click="openEdit(r)">
                Editar
              </button>
              <button 
                class="rounded border border-red-300 px-3 py-1 text-red-600 hover:bg-red-50" 
                @click="removeRow(r.id_product_transaction)"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Resumen -->
    <div v-if="rows.length > 0" class="flex gap-4 text-sm">
      <div class="rounded-lg border bg-gray-50 px-4 py-2">
        <span class="text-gray-600">Total movimientos:</span>
        <span class="ml-2 font-semibold">{{ rows.length }}</span>
      </div>
      <div class="rounded-lg border bg-green-50 px-4 py-2">
        <span class="text-green-700">Entradas:</span>
        <span class="ml-2 font-semibold text-green-800">
          {{ rows.filter(r => r.type_transaction === 0).length }}
        </span>
      </div>
      <div class="rounded-lg border bg-red-50 px-4 py-2">
        <span class="text-red-700">Salidas:</span>
        <span class="ml-2 font-semibold text-red-800">
          {{ rows.filter(r => r.type_transaction === 1).length }}
        </span>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="mx-4 w-full max-w-4xl rounded-2xl bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-semibold">
          {{ form.id_product_transaction ? "Editar movimiento" : "Nuevo movimiento" }}
        </h3>
        <TransactionForm 
          v-model="form" 
          :saving="saving" 
          :mode="form.id_product_transaction ? 'edit' : 'create'"
          @save="save" 
          @cancel="showModal = false" 
        />
      </div>
    </div>
  </section>
</template>