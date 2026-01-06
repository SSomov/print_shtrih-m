<script>
  import { onMount } from 'svelte'
  import { isAuthenticated, username, activeTab } from './lib/stores.js'
  import LoginForm from './components/LoginForm.svelte'
  import CheckForm from './components/CheckForm.svelte'
  import EgaisForm from './components/EgaisForm.svelte'
  import ProductsView from './components/ProductsView.svelte'
  import KktInfo from './components/KktInfo.svelte'
  import UsersView from './components/UsersView.svelte'
  import LogsView from './components/LogsView.svelte'
  import StatsView from './components/StatsView.svelte'
  import Logo from './components/Logo.svelte'

  let currentUsername = ''
  let currentAuth = false
  let currentTab = 'checks'

  $: currentUsername = $username
  $: currentAuth = $isAuthenticated
  $: currentTab = $activeTab

  onMount(() => {
    const token = localStorage.getItem('token')
    const savedUsername = localStorage.getItem('username')
    
    if (token && savedUsername) {
      isAuthenticated.set(true)
      username.set(savedUsername)
    }
  })

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    isAuthenticated.set(false)
    username.set('')
    activeTab.set('checks')
  }

  function handleMenuSelect(tab) {
    activeTab.set(tab)
  }
</script>

<div class="min-h-screen bg-gray-50">
  {#if !currentAuth}
    <LoginForm />
  {:else}
    <div class="flex flex-col h-screen">
      <!-- Header -->
      <header class="bg-primary-500 text-white shadow-md">
        <div class="flex items-center justify-between px-4 h-16">
          <div class="flex items-center gap-3">
            <Logo />
            <span class="text-lg font-semibold">Ресторан</span>
          </div>
          
          <nav class="flex-1 flex items-center justify-center gap-1 overflow-x-auto">
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'checks' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('checks')}
            >
              Чеки
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'egais' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('egais')}
            >
              ЕГАИС
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'products' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('products')}
            >
              Товары
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'kkt' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('kkt')}
            >
              ККТ
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'users' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('users')}
            >
              Пользователи
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'logs' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('logs')}
            >
              Логи
            </button>
            <button
              class="px-4 py-2 rounded-md transition-colors {currentTab === 'stats' ? 'bg-primary-600' : 'hover:bg-primary-600'}"
              on:click={() => handleMenuSelect('stats')}
            >
              Статистика
            </button>
          </nav>
          
          <div class="flex items-center gap-3 ml-4">
            <span class="text-sm">{currentUsername}</span>
            <button
              class="px-3 py-1 text-sm bg-danger-500 hover:bg-danger-600 rounded-md transition-colors"
              on:click={handleLogout}
            >
              Выход
            </button>
          </div>
        </div>
      </header>
      
      <!-- Main Content -->
      <main class="flex-1 overflow-auto p-5">
        {#if currentTab === 'checks'}
          <CheckForm />
        {:else if currentTab === 'egais'}
          <EgaisForm />
        {:else if currentTab === 'products'}
          <ProductsView />
        {:else if currentTab === 'kkt'}
          <KktInfo />
        {:else if currentTab === 'users'}
          <UsersView />
        {:else if currentTab === 'logs'}
          <LogsView />
        {:else if currentTab === 'stats'}
          <StatsView />
        {/if}
      </main>
    </div>
  {/if}
</div>

