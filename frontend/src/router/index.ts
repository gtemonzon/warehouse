// frontend/src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

// Productos
const ProductsList = () => import("../views/ProductsList.vue");
// Almacenes
const WarehousesList = () => import("../views/WarehousesList.vue");
// Kits
const KitsList = () => import("../views/KitsList.vue");
// Transacciones
const TransactionsList = () => import("../views/TransactionsList.vue");

// Si en algún momento vuelves a usar formularios por ruta, descomenta:
// const ProductForm = () => import("../views/ProductForm.vue");
// const WarehouseForm = () => import("../views/WarehouseForm.vue");

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/products" },

  // Productos
  { path: "/products", name: "products", component: ProductsList },
  // { path: "/products/new", name: "product-new", component: ProductForm },
  // { path: "/products/:id", name: "product-edit", component: ProductForm, props: true },

  // Almacenes
  { path: "/warehouses", name: "warehouses", component: WarehousesList },
  // { path: "/warehouses/new", name: "warehouse-new", component: WarehouseForm },
  // { path: "/warehouses/:id", name: "warehouse-edit", component: WarehouseForm, props: true },
  
  //kits
  { path: "/kits", name: "kits", component: KitsList },
  //transactions
  { path: "/transactions", name: "transactions", component: TransactionsList },
  // 404 (catch-all)
  { path: "/:pathMatch(.*)*", redirect: "/products" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
