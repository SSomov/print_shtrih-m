<script>
import { onMount } from "svelte";
import { logsApi } from "../lib/api.js";

let activeTab = "checks";
let checkLogs = [];
let checkLoading = false;
const checkPage = 1;
const checkPageSize = 20;
let checkTotal = 0;
const checkStatus = "";

let egaisLogs = [];
let egaisLoading = false;
const egaisPage = 1;
const egaisPageSize = 20;
let egaisTotal = 0;
const egaisStatus = "";

let detailsVisible = false;
let detailsTitle = "";
let detailsContent = "";

onMount(() => {
	loadCheckLogs();
});

async function loadCheckLogs() {
	checkLoading = true;
	try {
		const params = {
			page: checkPage,
			limit: checkPageSize,
		};
		if (checkStatus) {
			params.status = checkStatus;
		}

		const result = await logsApi.getCheckLogs(params);
		if (result.data.status === "success") {
			checkLogs = result.data.data;
			checkTotal = result.data.pagination.total;
		}
	} catch (error) {
		alert("Ошибка: " + error.message);
	} finally {
		checkLoading = false;
	}
}

async function loadEgaisLogs() {
	egaisLoading = true;
	try {
		const params = {
			page: egaisPage,
			limit: egaisPageSize,
		};
		if (egaisStatus) {
			params.status = egaisStatus;
		}

		const result = await logsApi.getEgaisLogs(params);
		if (result.data.status === "success") {
			egaisLogs = result.data.data;
			egaisTotal = result.data.pagination.total;
		}
	} catch (error) {
		alert("Ошибка: " + error.message);
	} finally {
		egaisLoading = false;
	}
}

function handleTabClick(tab) {
	activeTab = tab;
	if (tab === "egais" && egaisLogs.length === 0) {
		loadEgaisLogs();
	}
}

function viewCheckDetails(row) {
	detailsTitle = `Детали чека #${row.id}`;
	detailsContent = JSON.stringify(row, null, 2);
	detailsVisible = true;
}

function viewEgaisDetails(row) {
	detailsTitle = `Детали ЕГАИС #${row.id}`;
	detailsContent = JSON.stringify(row, null, 2);
	detailsVisible = true;
}

function refreshLogs() {
	if (activeTab === "checks") {
		loadCheckLogs();
	} else {
		loadEgaisLogs();
	}
}

function formatDate(dateString) {
	return new Date(dateString).toLocaleString("ru-RU");
}

function getStatusType(status) {
	switch (status) {
		case "success":
			return "bg-success-100 text-success-700";
		case "error":
			return "bg-danger-100 text-danger-700";
		case "saved":
			return "bg-warning-100 text-warning-700";
		default:
			return "bg-gray-100 text-gray-700";
	}
}
</script>

<div class="card">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Просмотр логов</h2>
        <button class="btn btn-primary" on:click={refreshLogs}>
            Обновить
        </button>
    </div>

    <div class="border-b border-gray-200 mb-4">
        <div class="flex gap-4">
            <button
                class="px-4 py-2 border-b-2 transition-colors {activeTab ===
                'checks'
                    ? 'border-primary-500 text-primary-500'
                    : 'border-transparent text-gray-600 hover:text-gray-900'}"
                on:click={() => handleTabClick("checks")}
            >
                Логи чеков
            </button>
            <button
                class="px-4 py-2 border-b-2 transition-colors {activeTab ===
                'egais'
                    ? 'border-primary-500 text-primary-500'
                    : 'border-transparent text-gray-600 hover:text-gray-900'}"
                on:click={() => handleTabClick("egais")}
            >
                Логи ЕГАИС
            </button>
        </div>
    </div>

    {#if activeTab === "checks"}
        <div class="space-y-4">
            <div class="flex gap-4 items-center">
                <select
                    class="input w-auto"
                    bind:value={checkStatus}
                    on:change={loadCheckLogs}
                >
                    <option value="">Все</option>
                    <option value="success">Успешно</option>
                    <option value="error">Ошибка</option>
                </select>
                <input
                    type="number"
                    class="input w-24"
                    bind:value={checkPageSize}
                    min="10"
                    max="100"
                    on:change={loadCheckLogs}
                />
            </div>

            {#if checkLoading}
                <div class="text-center py-8">Загрузка...</div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="bg-gray-100">
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >ID</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Время</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Статус</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Сообщение</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Код результата</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Номер чека</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Фискальный признак</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Действия</th
                                >
                            </tr>
                        </thead>
                        <tbody>
                            {#each checkLogs as log}
                                <tr class="hover:bg-gray-50">
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{log.id}</td
                                    >
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{formatDate(log.timestamp)}</td
                                    >
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        <span
                                            class="px-2 py-1 rounded text-sm {getStatusType(
                                                log.status,
                                            )}"
                                        >
                                            {log.status}
                                        </span>
                                    </td>
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{log.message}</td
                                    >
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{log.result_code || "-"}</td
                                    >
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{log.document_number || "-"}</td
                                    >
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        {#if log.fiscal_sign}
                                            <span
                                                class="font-mono text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded"
                                            >
                                                {log.fiscal_sign}
                                            </span>
                                        {:else}
                                            <span class="text-gray-400 italic"
                                                >-</span
                                            >
                                        {/if}
                                    </td>
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        <button
                                            class="btn btn-secondary text-sm"
                                            on:click={() =>
                                                viewCheckDetails(log)}
                                            >Детали</button
                                        >
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                {#if checkTotal > 0}
                    <div class="flex justify-between items-center">
                        <div class="text-sm text-gray-600">
                            Показано {(checkPage - 1) * checkPageSize + 1} - {Math.min(
                                checkPage * checkPageSize,
                                checkTotal,
                            )} из {checkTotal}
                        </div>
                        <div class="flex gap-2">
                            <button
                                class="btn btn-secondary text-sm"
                                disabled={checkPage === 1}
                                on:click={() => {
                                    checkPage--;
                                    loadCheckLogs();
                                }}
                            >
                                Назад
                            </button>
                            <button
                                class="btn btn-secondary text-sm"
                                disabled={checkPage * checkPageSize >=
                                    checkTotal}
                                on:click={() => {
                                    checkPage++;
                                    loadCheckLogs();
                                }}
                            >
                                Вперед
                            </button>
                        </div>
                    </div>
                {/if}
            {/if}
        </div>
    {:else}
        <div class="space-y-4">
            <div class="flex gap-4 items-center">
                <select
                    class="input w-auto"
                    bind:value={egaisStatus}
                    on:change={loadEgaisLogs}
                >
                    <option value="">Все</option>
                    <option value="success">Успешно</option>
                    <option value="error">Ошибка</option>
                    <option value="saved">Сохранено</option>
                </select>
                <input
                    type="number"
                    class="input w-24"
                    bind:value={egaisPageSize}
                    min="10"
                    max="100"
                    on:change={loadEgaisLogs}
                />
            </div>

            {#if egaisLoading}
                <div class="text-center py-8">Загрузка...</div>
            {:else}
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="bg-gray-100">
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >ID</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Время</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Статус</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >QR код</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Подпись</th
                                >
                                <th
                                    class="border border-gray-300 px-4 py-2 text-left"
                                    >Действия</th
                                >
                            </tr>
                        </thead>
                        <tbody>
                            {#each egaisLogs as log}
                                <tr class="hover:bg-gray-50">
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{log.id}</td
                                    >
                                    <td class="border border-gray-300 px-4 py-2"
                                        >{formatDate(log.timestamp)}</td
                                    >
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        <span
                                            class="px-2 py-1 rounded text-sm {getStatusType(
                                                log.status,
                                            )}"
                                        >
                                            {log.status}
                                        </span>
                                    </td>
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        {#if log.qr_code}
                                            <span class="font-mono text-xs"
                                                >{log.qr_code.substring(
                                                    0,
                                                    15,
                                                )}...</span
                                            >
                                        {:else}
                                            <span class="text-gray-400 italic"
                                                >-</span
                                            >
                                        {/if}
                                    </td>
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        {#if log.sign}
                                            <span
                                                class="font-mono text-xs bg-warning-50 text-warning-700 px-2 py-1 rounded"
                                            >
                                                {log.sign.substring(0, 12)}...
                                            </span>
                                        {:else}
                                            <span class="text-gray-400 italic"
                                                >-</span
                                            >
                                        {/if}
                                    </td>
                                    <td
                                        class="border border-gray-300 px-4 py-2"
                                    >
                                        <button
                                            class="btn btn-secondary text-sm"
                                            on:click={() =>
                                                viewEgaisDetails(log)}
                                            >Детали</button
                                        >
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                {#if egaisTotal > 0}
                    <div class="flex justify-between items-center">
                        <div class="text-sm text-gray-600">
                            Показано {(egaisPage - 1) * egaisPageSize + 1} - {Math.min(
                                egaisPage * egaisPageSize,
                                egaisTotal,
                            )} из {egaisTotal}
                        </div>
                        <div class="flex gap-2">
                            <button
                                class="btn btn-secondary text-sm"
                                disabled={egaisPage === 1}
                                on:click={() => {
                                    egaisPage--;
                                    loadEgaisLogs();
                                }}
                            >
                                Назад
                            </button>
                            <button
                                class="btn btn-secondary text-sm"
                                disabled={egaisPage * egaisPageSize >=
                                    egaisTotal}
                                on:click={() => {
                                    egaisPage++;
                                    loadEgaisLogs();
                                }}
                            >
                                Вперед
                            </button>
                        </div>
                    </div>
                {/if}
            {/if}
        </div>
    {/if}
</div>

<!-- Диалог деталей -->
{#if detailsVisible}
    <div
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
        <div class="card w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">{detailsTitle}</h3>
                <button
                    class="btn btn-secondary"
                    on:click={() => (detailsVisible = false)}>Закрыть</button
                >
            </div>
            <pre
                class="bg-gray-100 p-4 rounded overflow-x-auto text-sm">{detailsContent}</pre>
        </div>
    </div>
{/if}
