<script>
    import { logsApi } from "../lib/api.js";
    import { onMount } from "svelte";

    let loading = false;
    let stats = null;

    onMount(() => {
        loadStats();
    });

    async function loadStats() {
        loading = true;
        try {
            const result = await logsApi.getStats();
            if (result.data.status === "success") {
                stats = result.data;
            }
        } catch (error) {
            alert("Ошибка: " + error.message);
        } finally {
            loading = false;
        }
    }

    function getSuccessRate(data) {
        if (data.total === 0) return 0;
        return Math.round((data.success / data.total) * 100);
    }

    function getSuccessRateType(data) {
        const rate = getSuccessRate(data);
        if (rate >= 90) return "bg-success-100 text-success-700";
        if (rate >= 70) return "bg-warning-100 text-warning-700";
        return "bg-danger-100 text-danger-700";
    }
</script>

<div class="card">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Статистика</h2>
        <button class="btn btn-primary" on:click={loadStats} disabled={loading}>
            {loading ? "Загрузка..." : "Обновить"}
        </button>
    </div>

    {#if loading}
        <div class="text-center py-8">Загрузка...</div>
    {:else if stats}
        <div class="grid grid-cols-2 gap-4">
            <!-- Чеки -->
            <div class="card">
                <h3 class="text-lg font-semibold mb-4">Чеки</h3>
                <div class="space-y-3">
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600"
                            >Всего чеков:</span
                        >
                        <span
                            class="px-3 py-1 bg-gray-100 text-gray-700 rounded"
                            >{stats.checks.total}</span
                        >
                    </div>
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600">Успешно:</span>
                        <span
                            class="px-3 py-1 bg-success-100 text-success-700 rounded"
                            >{stats.checks.success}</span
                        >
                    </div>
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600">Ошибки:</span>
                        <span
                            class="px-3 py-1 bg-danger-100 text-danger-700 rounded"
                            >{stats.checks.error}</span
                        >
                    </div>
                    <div class="flex justify-between items-center py-2">
                        <span class="font-medium text-gray-600"
                            >Процент успеха:</span
                        >
                        <span
                            class="px-3 py-1 rounded {getSuccessRateType(
                                stats.checks,
                            )}"
                        >
                            {getSuccessRate(stats.checks)}%
                        </span>
                    </div>
                </div>
            </div>

            <!-- ЕГАИС -->
            <div class="card">
                <h3 class="text-lg font-semibold mb-4">ЕГАИС</h3>
                <div class="space-y-3">
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600"
                            >Всего отправок:</span
                        >
                        <span
                            class="px-3 py-1 bg-gray-100 text-gray-700 rounded"
                            >{stats.egais.total}</span
                        >
                    </div>
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600">Успешно:</span>
                        <span
                            class="px-3 py-1 bg-success-100 text-success-700 rounded"
                            >{stats.egais.success}</span
                        >
                    </div>
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600">Ошибки:</span>
                        <span
                            class="px-3 py-1 bg-danger-100 text-danger-700 rounded"
                            >{stats.egais.error}</span
                        >
                    </div>
                    <div
                        class="flex justify-between items-center py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600">Сохранено:</span
                        >
                        <span
                            class="px-3 py-1 bg-warning-100 text-warning-700 rounded"
                            >{stats.egais.saved}</span
                        >
                    </div>
                    <div class="flex justify-between items-center py-2">
                        <span class="font-medium text-gray-600"
                            >Процент успеха:</span
                        >
                        <span
                            class="px-3 py-1 rounded {getSuccessRateType(
                                stats.egais,
                            )}"
                        >
                            {getSuccessRate(stats.egais)}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="text-center py-8 text-gray-500">
            Нет данных для отображения
        </div>
    {/if}
</div>
