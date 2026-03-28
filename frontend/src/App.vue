<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <RouterView />
  </div>
</template>

<style>
.app-container {
  height: 100dvh;
  width: 100dvw;
  max-height: 100dvh;
  max-width: 100dvw;
  min-height: 100dvh;
  min-width: 100dvw;
  overflow: hidden;
  overscroll-behavior: none;
}
</style>
