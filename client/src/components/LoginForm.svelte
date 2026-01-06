<script>
import { authApi } from "../lib/api.js";
import { isAuthenticated, username } from "../lib/stores.js";

const loginForm = {
	username: "",
	password: "",
};
let loading = false;
let errorMessage = "";

async function handleLogin() {
	if (!loginForm.username || !loginForm.password) {
		errorMessage = "Заполните все поля";
		return;
	}

	loading = true;
	errorMessage = "";

	try {
		const response = await authApi.login(
			loginForm.username,
			loginForm.password
		);

		if (response.data.status === "success") {
			localStorage.setItem("token", response.data.token);
			localStorage.setItem("username", response.data.username);
			isAuthenticated.set(true);
			username.set(response.data.username);
			errorMessage = "";
		} else {
			errorMessage = response.data.message || "Ошибка авторизации";
		}
	} catch (error) {
		errorMessage =
			error.response?.data?.message || "Ошибка подключения к серверу";
	} finally {
		loading = false;
	}
}

function handleKeyPress(event) {
	if (event.key === "Enter") {
		handleLogin();
	}
}
</script>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-purple-600">
  <div class="card w-full max-w-md">
    <h2 class="text-2xl font-bold text-center text-primary-500 mb-6">Авторизация</h2>
    
    <form on:submit|preventDefault={handleLogin} class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя</label>
        <input
          type="text"
          class="input"
          bind:value={loginForm.username}
          on:keypress={handleKeyPress}
          placeholder="Введите имя пользователя"
        />
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
        <input
          type="password"
          class="input"
          bind:value={loginForm.password}
          on:keypress={handleKeyPress}
          placeholder="Введите пароль"
        />
      </div>
      
      <button
        type="submit"
        class="btn btn-primary w-full"
        disabled={loading}
      >
        {loading ? "Вход..." : "Войти"}
      </button>
    </form>
    
    {#if errorMessage}
      <div class="mt-4 p-3 bg-danger-50 border border-danger-200 rounded-md text-danger-700 text-sm">
        {errorMessage}
      </div>
    {/if}
  </div>
</div>

