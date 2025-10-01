<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import api from "../api";

type Option = { value: number; label: string };
type KitComposition = { 
  id_product: number; 
  product_name: string; 
  quantaty: number;
  stock?: number; // Existencias disponibles
};

type Form = {
  id_product_transaction?: number;
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

const title = computed(() =>
  props.mode === "edit" ? "Editar movimiento" : "Nuevo movimiento"
);

// Estado
const movementType = ref<"product" | "kit">("product");
const products = ref<Option[]>([]);
const warehouses = ref<Option[]>([]);
const kits = ref<Option[]>([]);
const kitComposition = ref<KitComposition[]>([]);
const productStock = ref<number | null>(null);
const error = ref<string | null>(null);
const validationError = ref<string | null>(null);

// Validación: ¿hay stock suficiente para el kit?
const hasInsufficientStock = computed(() => {
  if (movementType.value !== "kit" || !model.value.quantaty_kit) return false;
  return kitComposition.value.some(item => {
    const needed = item.quantaty * (model.value.quantaty_kit || 0);
    return (item.stock || 0) < needed;
  });
});

// Validación: ¿la cantidad de producto excede el stock?
const productExceedsStock = computed(() => {
  if (movementType.value !== "product" || model.value.type_transaction !== 1) return false;
  if (!model.value.quantaty_products || productStock.value === null) return false;
  return model.value.quantaty_products > productStock.value;
});

// Validación general antes de guardar
const canSave = computed(() => {
  return !hasInsufficientStock.value && !productExceedsStock.value;
});

// Cargar opciones
async function loadOptions() {
  error.value = null;
  try {
    const [p, w, k] = await Promise.all([
      api.get("/products", { params: { limit: 200, skip: 0 } }),
      api.get("/warehouses", { params: { limit: 200, skip: 0 } }),
      api.get("/kits", { params: { limit: 200, skip: 0 } }).catch(() => ({ data: [] })),
    ]);
    products.value = (p.data || []).map((x: any) => ({ value: x.id_product, label: x.cname }));
    warehouses.value = (w.data || []).map((x: any) => ({ value: x.id_warehouse, label: x.cname }));
    kits.value = (k.data || []).map((x: any) => ({ value: x.id_kit, label: x.cname }));
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e.message || "Error cargando opciones";
  }
}

// Cargar stock del producto individual
async function loadProductStock() {
  productStock.value = null;
  validationError.value = null;
  
  if (movementType.value === "product" && 
      model.value.type_transaction === 1 && 
      model.value.id_product && 
      model.value.id_warehouse) {
    try {
      const { data } = await api.get(`/transactions/inventory/${model.value.id_warehouse}/${model.value.id_product}`);
      productStock.value = data.stock;
    } catch (e: any) {
      error.value = "Error obteniendo existencias";
    }
  }
}

// Cargar composición del kit con existencias
async function loadKitComposition() {
  if (!model.value.id_kit || !model.value.id_warehouse) {
    kitComposition.value = [];
    return;
  }

  try {
    const { data } = await api.get<KitComposition[]>(`/kits/${model.value.id_kit}/composition`);
    
    // Cargar existencias de cada producto
    const withStock = await Promise.all(
      data.map(async (item) => {
        try {
          const stockData = await api.get(`/transactions/inventory/${model.value.id_warehouse}/${item.id_product}`);
          return { ...item, stock: stockData.data.stock };
        } catch {
          return { ...item, stock: 0 };
        }
      })
    );
    
    kitComposition.value = withStock;
  } catch (e: any) {
    error.value = "Error cargando composición del kit";
    kitComposition.value = [];
  }
}

// Watchers
watch(() => model.value.id_kit, () => {
  if (movementType.value === "kit") {
    loadKitComposition();
  }
});

watch(() => model.value.id_warehouse, () => {
  if (movementType.value === "kit" && model.value.id_kit) {
    loadKitComposition();
  } else if (movementType.value === "product") {
    loadProductStock();
  }
});

watch([() => model.value.id_product, () => model.value.type_transaction], () => {
  if (movementType.value === "product") {
    loadProductStock();
  }
});

watch(movementType, (newType) => {
  validationError.value = null;
  if (newType === "product") {
    model.value.id_kit = null;
    model.value.quantaty_kit = null;
    kitComposition.value = [];
  } else {
    // Para kits solo salidas
    model.value.type_transaction = 1;
    model.value.id_product = null;
    model.value.quantaty_products = null;
    productStock.value = null;
  }
});

function handleSave() {
  validationError.value = null;
  
  if (hasInsufficientStock.value) {
    validationError.value = "No existen disponibilidades de productos para la cantidad de kits que se requiere";
    return;
  }
  
  if (productExceedsStock.value) {
    validationError.value = `La cantidad excede las existencias disponibles (${productStock.value})`;
    return;
  }
  
  emit("save");
}

function fmtDate(v?: string | null) {
  if (!v) return "—";
  const d = new Date(v);
  if (!isNaN(d.getTime())) {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }
  return v;
}

onMounted(loadOptions);
</script>

<template>
  <form @submit.prevent="handleSave" class="space-y-4">
    <div v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ error }}
    </div>

    <div v-if="validationError" class="rounded-lg border border-orange-200 bg-orange-50 px-3 py-2 text-sm text-orange-700">
      {{ validationError }}
    </div>

    <!-- Tabs para elegir tipo de movimiento -->
    <div class="flex gap-2 border-b pb-2">
      <button
        type="button"
        @click="movementType = 'product'"
        :class="[
          'px-4 py-2 rounded-t-lg font-medium transition-colors',
          movementType === 'product'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        Producto Individual
      </button>
      <button
        type="button"
        @click="movementType = 'kit'"
        :class="[
          'px-4 py-2 rounded-t-lg font-medium transition-colors',
          movementType === 'kit'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
      >
        Kit Completo (Solo Salidas)
      </button>
    </div>

    <!-- Campos comunes -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <label class="block space-y-1">
        <span class="text-sm">Almacén *</span>
        <select v-model.number="model.id_warehouse" required
                class="w-full rounded-lg border px-3 py-2">
          <option :value="null" disabled>— Selecciona —</option>
          <option v-for="o in warehouses" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </label>

      <label v-if="movementType === 'product'" class="block space-y-1">
        <span class="text-sm">Tipo de movimiento *</span>
        <select v-model.number="model.type_transaction" required class="w-full rounded-lg border px-3 py-2">
          <option :value="0">Entrada (suma)</option>
          <option :value="1">Salida (resta)</option>
        </select>
      </label>
      <div v-else class="block space-y-1">
        <span class="text-sm">Tipo de movimiento</span>
        <div class="w-full rounded-lg border bg-gray-50 px-3 py-2 text-gray-600">
          Salida (resta) - Los kits solo pueden salir
        </div>
      </div>
    </div>

    <!-- Campos específicos: Producto Individual -->
    <div v-if="movementType === 'product'" class="space-y-4">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label class="block space-y-1">
          <span class="text-sm">Producto *</span>
          <select v-model.number="model.id_product" required
                  class="w-full rounded-lg border px-3 py-2">
            <option :value="null" disabled>— Selecciona —</option>
            <option v-for="o in products" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>

        <label class="block space-y-1">
          <span class="text-sm">Cantidad *</span>
          <input v-model.number="model.quantaty_products" type="number" min="1" required
                 :class="[
                   'w-full rounded-lg border px-3 py-2 outline-none focus:ring-2',
                   productExceedsStock ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'
                 ]" />
        </label>
      </div>

      <!-- Mostrar existencias para salidas -->
      <div v-if="model.type_transaction === 1 && productStock !== null" 
           :class="[
             'rounded-lg border px-3 py-2 text-sm',
             productStock > 0 ? 'border-green-200 bg-green-50 text-green-800' : 'border-red-200 bg-red-50 text-red-800'
           ]">
        <strong>Existencias disponibles:</strong> {{ productStock }} unidad(es)
      </div>

      <label v-if="model.type_transaction === 0" class="block space-y-1">
        <span class="text-sm">Fecha de vencimiento (solo para entradas)</span>
        <input v-model="model.expiration_date" type="date"
               class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
      </label>
    </div>

    <!-- Campos específicos: Kit Completo -->
    <div v-else class="space-y-4">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label class="block space-y-1">
          <span class="text-sm">Kit *</span>
          <select v-model.number="model.id_kit" required
                  class="w-full rounded-lg border px-3 py-2">
            <option :value="null" disabled>— Selecciona —</option>
            <option v-for="o in kits" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </label>

        <label class="block space-y-1">
          <span class="text-sm">Cantidad de kits *</span>
          <input v-model.number="model.quantaty_kit" type="number" min="1" required
                 :class="[
                   'w-full rounded-lg border px-3 py-2 outline-none focus:ring-2',
                   hasInsufficientStock ? 'border-red-500 focus:ring-red-500' : 'focus:ring-blue-500'
                 ]" />
        </label>
      </div>

      <!-- Mostrar composición del kit con validación de stock -->
      <div v-if="kitComposition.length > 0" class="rounded-lg border bg-blue-50 p-3">
        <p class="mb-2 text-sm font-medium text-blue-900">Productos en este kit:</p>
        <ul class="space-y-1 text-sm">
          <li v-for="item in kitComposition" :key="item.id_product"
              :class="[
                'flex items-center justify-between',
                item.stock !== undefined && model.quantaty_kit && (item.quantaty * model.quantaty_kit > item.stock)
                  ? 'text-red-700 font-medium'
                  : 'text-blue-800'
              ]">
            <span>
              • {{ item.product_name }} - <strong>{{ item.quantaty }}</strong> unidad(es) por kit
              <span v-if="model.quantaty_kit" class="ml-2">
                (Total necesario: {{ item.quantaty * model.quantaty_kit }})
              </span>
            </span>
            <span v-if="item.stock !== undefined" 
                  :class="[
                    'ml-3 rounded px-2 py-0.5 text-xs font-medium',
                    model.quantaty_kit && (item.quantaty * model.quantaty_kit > item.stock)
                      ? 'bg-red-100 text-red-800'
                      : 'bg-green-100 text-green-800'
                  ]">
              Stock: {{ item.stock }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Campos opcionales -->
    <label class="block space-y-1">
      <span class="text-sm">Descripción</span>
      <textarea v-model="model.description" rows="3"
                class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
    </label>

    <label class="block space-y-1">
      <span class="text-sm">ID Planificación/Solicitud (opcional)</span>
      <input v-model.number="model.id_planification_expense_request" type="number" min="0"
             class="w-full rounded-lg border px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500" />
    </label>

    <!-- Botones -->
    <div class="flex gap-2">
      <button 
        type="submit"
        :disabled="saving || !canSave"
        class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
        {{ saving ? "Guardando…" : "Guardar" }}
      </button>
      <button type="button" @click="emit('cancel')" class="rounded-lg border px-4 py-2 hover:bg-gray-50">
        Cancelar
      </button>
    </div>

    <!-- Metadatos -->
    <div v-if="model.add_date" class="mt-2 space-y-1 text-sm text-gray-600">
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