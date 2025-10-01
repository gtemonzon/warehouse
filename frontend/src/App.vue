<!-- frontend/src/App.vue -->
<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from "vue-router";
const route = useRoute();
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white">
      <nav class="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
        <RouterLink class="font-semibold hover:underline" to="/products">Productos</RouterLink>
        <RouterLink class="font-semibold hover:underline" to="/warehouses">Almacenes</RouterLink>
        <RouterLink class="font-semibold hover:underline" to="/kits">Kits</RouterLink>
        <RouterLink class="font-semibold hover:underline" to="/transactions">Movimientos</RouterLink>
      </nav>
    </header> 
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
