<template>
  <div class="logo">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Тарелка -->
      <ellipse cx="20" cy="26" rx="18" ry="8" fill="#409EFF" opacity="0.2"/>
      <ellipse cx="20" cy="26" rx="16" ry="6" fill="#409EFF" opacity="0.3"/>
      
      <!-- Еда на тарелке -->
      <circle cx="18" cy="24" r="3" fill="#67C23A"/>
      <circle cx="22" cy="24" r="3" fill="#F56C6C"/>
      <circle cx="20" cy="21" r="2.5" fill="#E6A23C"/>
      
      <!-- Дым -->
      <path d="M12 18 Q11 15 13 13" stroke="#909399" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M16 15 Q15 12 17 10" stroke="#909399" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M20 16 Q19 13 21 11" stroke="#909399" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M24 15 Q23 12 25 10" stroke="#909399" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M28 18 Q27 15 29 13" stroke="#909399" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      
      <!-- Блюдо -->
      <ellipse cx="20" cy="26" rx="18" ry="8" fill="none" stroke="#409EFF" stroke-width="2"/>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'Logo'
}
</script>

<style scoped>
.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.logo:hover {
  transform: scale(1.05);
}

.logo svg {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}
</style>
