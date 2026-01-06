<script>
    import { logsApi } from "../lib/api.js";
    import { onMount } from "svelte";

    let loading = false;
    let error = null;
    let kktInfo = null;
    let sessionParams = null;

    onMount(() => {
        loadKktInfo();
    });

    async function loadKktInfo() {
        loading = true;
        error = null;
        try {
            const result = await logsApi.getKktInfo();
            if (result.data.status === "success") {
                kktInfo = result.data.kkt_info;
            } else {
                error = result.data.error || "Ошибка получения данных ККТ";
            }

            try {
                const sessionResult = await logsApi.getFnSessionParams();
                if (sessionResult.data.status === "success") {
                    sessionParams = sessionResult.data.session_params;
                }
            } catch (sessionError) {
                console.warn(
                    "Не удалось загрузить параметры смены:",
                    sessionError.message,
                );
            }
        } catch (err) {
            error = "Ошибка: " + err.message;
        } finally {
            loading = false;
        }
    }

    function formatDate(dateString) {
        if (!dateString) return "-";
        return new Date(dateString).toLocaleString("ru-RU");
    }

    function getExpirationClass(expirationDate) {
        if (!expirationDate) return "";

        const expiration = new Date(expirationDate);
        const now = new Date();
        const daysUntilExpiration = Math.ceil(
            (expiration - now) / (1000 * 60 * 60 * 24),
        );

        if (daysUntilExpiration < 0)
            return "bg-danger-50 text-danger-700 border-danger-200";
        if (daysUntilExpiration <= 30)
            return "bg-warning-50 text-warning-700 border-warning-200";
        if (daysUntilExpiration <= 90)
            return "bg-primary-50 text-primary-700 border-primary-200";
        return "bg-success-50 text-success-700 border-success-200";
    }

    function getSessionStateText(state) {
        if (state === null || state === undefined) return "Неизвестно";
        switch (state) {
            case 0:
                return "Смена закрыта";
            case 1:
                return "Смена открыта";
            case 2:
                return "Смена истекла";
            default:
                return `Состояние ${state}`;
        }
    }

    function getSessionStateType(state) {
        if (state === null || state === undefined) return "info";
        switch (state) {
            case 0:
                return "bg-gray-100 text-gray-700";
            case 1:
                return "bg-success-100 text-success-700";
            case 2:
                return "bg-warning-100 text-warning-700";
            default:
                return "bg-gray-100 text-gray-700";
        }
    }
</script>

<div class="card">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Информация о ККТ</h2>
        <button
            class="btn btn-primary"
            on:click={loadKktInfo}
            disabled={loading}
        >
            {loading ? "Загрузка..." : "Обновить"}
        </button>
    </div>

    {#if loading}
        <div class="text-center py-8">Загрузка...</div>
    {:else if error}
        <div
            class="p-4 bg-danger-50 border border-danger-200 rounded-md text-danger-700"
        >
            {error}
        </div>
    {:else if kktInfo}
        <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <!-- Статус ККТ -->
                <div class="card">
                    <h3 class="text-lg font-semibold text-primary-500 mb-4">
                        Статус ККТ
                    </h3>
                    <div class="space-y-2">
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Номер документа:</span
                            >
                            <span class="font-mono text-sm"
                                >{kktInfo.ECRStatus?.DocumentNumber ||
                                    "-"}</span
                            >
                        </div>
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Код результата:</span
                            >
                            <span class="font-mono text-sm"
                                >{kktInfo.ECRStatus?.ResultCode || "-"}</span
                            >
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="font-medium text-gray-600"
                                >Описание:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.ECRStatus?.ResultCodeDescription ||
                                    "-"}</span
                            >
                        </div>
                    </div>
                </div>

                <!-- Статус ФН -->
                <div class="card">
                    <h3 class="text-lg font-semibold text-primary-500 mb-4">
                        Статус ФН
                    </h3>
                    <div class="space-y-2">
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Серийный номер:</span
                            >
                            <span
                                class="font-mono text-sm bg-primary-50 text-primary-700 px-2 py-1 rounded"
                            >
                                {kktInfo.FNStatus?.SerialNumber || "-"}
                            </span>
                        </div>
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Номер ФД:</span
                            >
                            <span class="font-mono text-sm"
                                >{kktInfo.FNStatus?.DocumentNumber || "-"}</span
                            >
                        </div>
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Состояние ФН:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.FNStatus?.FNLifeState || "-"}</span
                            >
                        </div>
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Состояние смены:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.FNStatus?.FNSessionState || "-"}</span
                            >
                        </div>
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600">Дата:</span>
                            <span class="text-sm"
                                >{formatDate(kktInfo.FNStatus?.Date)}</span
                            >
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="font-medium text-gray-600">Время:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.FNStatus?.Time || "-"}</span
                            >
                        </div>
                    </div>
                </div>
            </div>

            <!-- Срок действия ФН -->
            <div class="card">
                <h3 class="text-lg font-semibold text-primary-500 mb-4">
                    Срок действия ФН
                </h3>
                <div class="space-y-2">
                    <div
                        class="flex justify-between py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600"
                            >Дата истечения:</span
                        >
                        <span
                            class="font-semibold px-3 py-1 rounded border {getExpirationClass(
                                kktInfo.FNExpiration?.Date,
                            )}"
                        >
                            {formatDate(kktInfo.FNExpiration?.Date)}
                        </span>
                    </div>
                    <div
                        class="flex justify-between py-2 border-b border-gray-200"
                    >
                        <span class="font-medium text-gray-600"
                            >Код результата:</span
                        >
                        <span class="font-mono text-sm"
                            >{kktInfo.FNExpiration?.ResultCode || "-"}</span
                        >
                    </div>
                    <div class="flex justify-between py-2">
                        <span class="font-medium text-gray-600">Описание:</span>
                        <span class="text-sm"
                            >{kktInfo.FNExpiration?.ResultCodeDescription ||
                                "-"}</span
                        >
                    </div>
                </div>
            </div>

            <!-- Фискализация ФН -->
            <div class="card">
                <h3 class="text-lg font-semibold text-primary-500 mb-4">
                    Фискализация ФН
                </h3>
                <div class="grid grid-cols-3 gap-4">
                    <div class="space-y-2">
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600">ИНН:</span>
                            <span class="font-mono text-sm"
                                >{kktInfo.FNFiscalization?.INN || "-"}</span
                            >
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="font-medium text-gray-600"
                                >Рег. номер ККТ:</span
                            >
                            <span
                                class="font-mono text-sm bg-primary-50 text-primary-700 px-2 py-1 rounded"
                            >
                                {kktInfo.FNFiscalization
                                    ?.KKTRegistrationNumber || "-"}
                            </span>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Номер ФД:</span
                            >
                            <span class="font-mono text-sm"
                                >{kktInfo.FNFiscalization?.DocumentNumber ||
                                    "-"}</span
                            >
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="font-medium text-gray-600"
                                >Фискальный признак:</span
                            >
                            <span
                                class="font-mono text-sm bg-success-50 text-success-700 px-2 py-1 rounded"
                            >
                                {kktInfo.FNFiscalization?.FiscalSign || "-"}
                            </span>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div
                            class="flex justify-between py-2 border-b border-gray-200"
                        >
                            <span class="font-medium text-gray-600"
                                >Код налогообложения:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.FNFiscalization?.TaxType || "-"}</span
                            >
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="font-medium text-gray-600"
                                >Режим работы:</span
                            >
                            <span class="text-sm"
                                >{kktInfo.FNFiscalization?.WorkMode ||
                                    "-"}</span
                            >
                        </div>
                    </div>
                </div>
            </div>

            <!-- Параметры текущей смены -->
            {#if sessionParams}
                <div class="card">
                    <h3 class="text-lg font-semibold text-primary-500 mb-4">
                        Параметры текущей смены
                    </h3>
                    <div class="grid grid-cols-3 gap-4">
                        <div>
                            <span class="font-medium text-gray-600"
                                >Состояние смены:</span
                            >
                            <span
                                class="ml-2 px-3 py-1 rounded text-sm {getSessionStateType(
                                    sessionParams.fn_session_state,
                                )}"
                            >
                                {getSessionStateText(
                                    sessionParams.fn_session_state,
                                )}
                            </span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-600"
                                >Номер смены:</span
                            >
                            <span class="ml-2 font-mono text-sm"
                                >{sessionParams.session_number || "-"}</span
                            >
                        </div>
                        <div>
                            <span class="font-medium text-gray-600"
                                >Номер чека:</span
                            >
                            <span class="ml-2 font-mono text-sm"
                                >{sessionParams.receipt_number || "-"}</span
                            >
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    {/if}
</div>
