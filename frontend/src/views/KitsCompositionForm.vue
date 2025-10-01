<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import api from "../api";

type Product = {
  id_product: number;
  code?: number | null;
  cname: string;
};

type Row = {
  id_kit_composition: number;
  id_product: number;
  quantaty: number;
  product_code?: number | null;
  product_name?: string | null;
};

const props = defineProps<{
  kitId: number;
}>();

const products = ref<Product[]>([]);
const rows = ref<Row[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const form = ref<{
  id_kit_composition?: number | null;
  id_product: number | null;
  quantaty: number | null;
}>({
  id_kit_composition: null,
  id_product: null,
  quantaty: null,
});
const saving = ref(false);

const productsMap = computed(() => {
  const m = new Map<number, Product>();
  for (const p of products.value) m.set(p.id_product, p);
  return m;
});

function labelForProduct(id: number | null) {
  if (!id) return "—";
  const p = productsMap.value.get(id);
  if (!p) return `#${id}`;
  return `${p.code ?? "—"} — ${p.cname}`;
}

async function loadProducts() {
  try {
    const { data } = await api.get<Product[]>("/products", {  // ✅ SIN barra final
      params: { limit: 200, skip: 0 },
    });
    products.value = data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Error cargando productos";
  }
}

async function loadRows() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get<Row[]>(`/kits/${props.kitId}/composition`);
    rows.value = data;
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  form.value = { id_kit_composition: null, id_product: null, quantaty: null };
}

function editRow(r: Row) {
  form.value = {
    id_kit_composition: r.id_kit_composition,
    id_product: r.id_product,
    quantaty: r.quantaty,
  };
}

async function removeRow(id: number) {
  if (!confirm("¿Eliminar producto del kit?")) return;
  try {
    await api.delete(`/kits/${props.kitId}/composition/${id}`);
    await loadRows();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  }
}

async function save() {
  if (!form.value.id_product || !form.value.quantaty) return;
  saving.value = true;
  error.value = null;
  try {
    if (form.value.id_kit_composition) {
      await api.put(
        `/kits/${props.kitId}/composition/${form.value.id_kit_composition}`,
        { quantaty: Number(form.value.quantaty), mod_user: 1 }
      );
    } else {
      await api.post(`/kits/${props.kitId}/composition`, {
        id_product: Number(form.value.id_product),
        quantaty: Number(form.value.quantaty),
        add_user: 1,
      });
    }
    await loadRows();
    resetForm();
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Network Error";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadProducts(), loadRows()]);
});
</script>

<template>
  <div class="space-y-4">
    <div
      v-if="error"
      class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
    >
      {{ error }}
    </div>

    <!-- Formulario alta/edición -->
    <form @submit.prevent="save" class="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <label class="space-y-1">
        <span class="text-sm">Producto</span>
        <select
          v-model.number="form.id_product"
          class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
          required
        >
          <option :value="null" disabled>Selecciona…</option>
          <option v-for="p in products" :key="p.id_product" :value="p.id_product">
            {{ p.code ?? "—" }} — {{ p.cname }}
          </option>
        </select>
      </label>
      <label class="space-y-1">
        <span class="text-sm">Cantidad</span>
        <input
          v-model.number="form.quantaty"
          type="number"
          min="1"
          class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </label>
      <div class="flex items-end gap-2">
        <button
          :disabled="saving"
          class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {{ form.id_kit_composition ? "Actualizar" : "Agregar" }}
        </button>
        <button type="button" class="rounded-lg border px-4 py-2 hover:bg-gray-50" @click="resetForm">
          Limpiar
        </button>
      </div>
    </form>

    <!-- Tabla -->
    <div class="overflow-x-auto rounded-lg border bg-white">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 text-left">
          <tr>
            <th class="px-3 py-2">Producto</th>
            <th class="px-3 py-2">Cantidad</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="3" class="px-3 py-6 text-center text-gray-500">Cargando…</td>
          </tr>
          <tr v-else-if="rows.length === 0">
            <td colspan="3" class="px-3 py-6 text-center text-gray-500">Sin productos en este kit</td>
          </tr>
          <tr v-for="r in rows" :key="r.id_kit_composition" class="border-t">
            <td class="px-3 py-2">
              {{ r.product_name ?? labelForProduct(r.id_product) }}
            </td>
            <td class="px-3 py-2">{{ r.quantaty }}</td>
            <td class="px-3 py-2 space-x-2 text-right">
              <button class="rounded border px-3 py-1 hover:bg-gray-50" @click="editRow(r)">
                Editar
              </button>
              <button
                class="rounded border border-red-300 px-3 py-1 text-red-600 hover:bg-red-50"
                @click="removeRow(r.id_kit_composition)"
              >
                Eliminar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>