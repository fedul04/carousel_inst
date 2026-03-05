<script setup lang="ts">
import { statusClass, statusLabel } from "~/utils/status"

const props = defineProps<{
  value: string
}>()

const label = computed(() => statusLabel(props.value))
const cls = computed(() => statusClass(props.value))
</script>

<template>
  <span class="status-badge" :class="cls">{{ label }}</span>
</template>

