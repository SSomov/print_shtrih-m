<script>
import { onMount } from "svelte";
import { usersApi } from "../lib/api.js";

let users = [];
let loading = false;
let dialogVisible = false;
let editMode = false;
let userForm = {
	username: "",
	password: "",
	is_active: true,
};

onMount(() => {
	loadUsers();
});

async function loadUsers() {
	loading = true;
	try {
		const response = await usersApi.getUsers();
		users = response.data.data;
	} catch (error) {
		alert(
			"Ошибка загрузки пользователей: " +
				(error.response?.data?.message || error.message)
		);
	} finally {
		loading = false;
	}
}

function showAddDialog() {
	editMode = false;
	userForm = { username: "", password: "", is_active: true };
	dialogVisible = true;
}

function editUser(user) {
	editMode = true;
	userForm = {
		id: user.id,
		username: user.username,
		password: "",
		is_active: user.is_active,
	};
	dialogVisible = true;
}

async function saveUser() {
	if (!userForm.username) {
		alert("Введите имя пользователя");
		return;
	}

	if (!editMode && !userForm.password) {
		alert("Введите пароль");
		return;
	}

	try {
		const userData = {
			username: userForm.username,
			is_active: userForm.is_active,
		};

		if (userForm.password) {
			userData.password = userForm.password;
		}

		if (editMode) {
			await usersApi.updateUser(userForm.id, userData);
			alert("Пользователь обновлен");
		} else {
			await usersApi.createUser(userData);
			alert("Пользователь создан");
		}

		dialogVisible = false;
		await loadUsers();
	} catch (error) {
		alert("Ошибка сохранения: " + error.message);
	}
}

async function deleteUser(user) {
	if (
		!confirm(
			`Вы уверены, что хотите деактивировать пользователя "${user.username}"?`
		)
	) {
		return;
	}

	try {
		await usersApi.deleteUser(user.id);
		alert("Пользователь деактивирован");
		await loadUsers();
	} catch (error) {
		alert("Ошибка удаления: " + error.message);
	}
}

function formatDate(dateString) {
	if (!dateString) return "-";
	const date = new Date(dateString);
	return date.toLocaleString("ru-RU", {
		year: "numeric",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
	});
}
</script>

<div class="card">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Управление пользователями</h2>
        <button class="btn btn-primary" on:click={showAddDialog}>
            + Добавить пользователя
        </button>
    </div>

    {#if loading}
        <div class="text-center py-8">Загрузка...</div>
    {:else}
        <div class="overflow-x-auto">
            <table class="w-full border-collapse">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="border border-gray-300 px-4 py-2 text-left"
                            >Имя пользователя</th
                        >
                        <th class="border border-gray-300 px-4 py-2 text-left"
                            >Статус</th
                        >
                        <th class="border border-gray-300 px-4 py-2 text-left"
                            >Дата создания</th
                        >
                        <th class="border border-gray-300 px-4 py-2 text-left"
                            >Действия</th
                        >
                    </tr>
                </thead>
                <tbody>
                    {#each users as user}
                        <tr class="hover:bg-gray-50">
                            <td class="border border-gray-300 px-4 py-2"
                                >{user.username}</td
                            >
                            <td class="border border-gray-300 px-4 py-2">
                                {#if user.is_active}
                                    <span
                                        class="px-2 py-1 bg-success-100 text-success-700 rounded text-sm"
                                        >Активен</span
                                    >
                                {:else}
                                    <span
                                        class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
                                        >Деактивирован</span
                                    >
                                {/if}
                            </td>
                            <td class="border border-gray-300 px-4 py-2"
                                >{formatDate(user.created_at)}</td
                            >
                            <td class="border border-gray-300 px-4 py-2">
                                <div class="flex gap-2">
                                    <button
                                        class="text-primary-500 hover:text-primary-700"
                                        on:click={() => editUser(user)}
                                        >✏️</button
                                    >
                                    <button
                                        class="text-danger-500 hover:text-danger-700 {!user.is_active
                                            ? 'opacity-50 cursor-not-allowed'
                                            : ''}"
                                        on:click={() => deleteUser(user)}
                                        disabled={!user.is_active}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {/if}
</div>

<!-- Диалог создания/редактирования пользователя -->
{#if dialogVisible}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
        <div class="card w-full max-w-md">
            <h3 class="text-lg font-semibold mb-4">
                {editMode
                    ? "Редактировать пользователя"
                    : "Добавить пользователя"}
            </h3>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1"
                        >Имя пользователя *</label
                    >
                    <input
                        type="text"
                        class="input"
                        bind:value={userForm.username}
                    />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        {editMode ? "Новый пароль" : "Пароль"}
                        {editMode ? "" : "*"}
                    </label>
                    <input
                        type="password"
                        class="input"
                        bind:value={userForm.password}
                        placeholder={editMode
                            ? "Оставьте пустым, чтобы не менять"
                            : ""}
                    />
                </div>

                <div>
                    <label class="flex items-center gap-2">
                        <input
                            type="checkbox"
                            bind:checked={userForm.is_active}
                        />
                        <span>Активен</span>
                    </label>
                </div>
            </div>

            <div class="flex gap-3 mt-6">
                <button
                    class="btn btn-secondary flex-1"
                    on:click={() => (dialogVisible = false)}>Отмена</button
                >
                <button class="btn btn-primary flex-1" on:click={saveUser}
                    >Сохранить</button
                >
            </div>
        </div>
    </div>
{/if}
