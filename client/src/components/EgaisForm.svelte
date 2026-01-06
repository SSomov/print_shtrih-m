<script>
import { egaisApi } from "../lib/api.js";

let loading = false;
let form = {
	num: "",
	typedoc: "check",
	hall: "",
	table: "",
	create: new Date().toLocaleString("ru-RU"),
	waiter: "",
	employee_fio: "",
	employee_inn: "",
	employee_pos: "",
	alldiscount: "0",
	products: [
		{
			name: "",
			kolvo: "1",
			price: "0",
			GTIN: "",
			alc_code: "",
			qr: "",
			egais_mark_code: "",
			egais_id: "",
			mark: "1",
		},
	],
};

function addProduct() {
	form.products = [
		...form.products,
		{
			name: "",
			kolvo: 1,
			price: 0,
			GTIN: "",
			alc_code: "",
			qr: "",
			egais_mark_code: "",
			egais_id: "",
			mark: "1",
		},
	];
}

function removeProduct(index) {
	if (form.products.length > 1) {
		form.products = form.products.filter((_, i) => i !== index);
	}
}

async function submitEgais() {
	loading = true;
	try {
		const result = await egaisApi.sendCheck(form);

		if (result.data.message) {
			alert("ЕГАИС: " + result.data.message);
			resetForm();
		} else if (result.data.error) {
			alert("Ошибка: " + result.data.error);
		}
	} catch (error) {
		alert("Ошибка: " + error.message);
	} finally {
		loading = false;
	}
}

function resetForm() {
	form = {
		num: "",
		typedoc: "check",
		hall: "",
		table: "",
		create: new Date().toLocaleString("ru-RU"),
		waiter: "",
		employee_fio: "",
		employee_inn: "",
		employee_pos: "",
		alldiscount: "0",
		products: [
			{
				name: "",
				kolvo: "1",
				price: "0",
				GTIN: "",
				alc_code: "",
				qr: "",
				egais_mark_code: "",
				egais_id: "",
				mark: "1",
			},
		],
	};
}
</script>

<div class="card">
  <h2 class="card-header">Отправка в ЕГАИС</h2>
  
  <form on:submit|preventDefault={submitEgais} class="space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Номер заказа</label>
        <input type="text" class="input" bind:value={form.num} placeholder="Введите номер заказа" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Сотрудник ФИО</label>
        <input type="text" class="input" bind:value={form.employee_fio} placeholder="ФИО сотрудника" />
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ИНН сотрудника</label>
        <input type="text" class="input" bind:value={form.employee_inn} placeholder="ИНН сотрудника" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Должность</label>
        <input type="text" class="input" bind:value={form.employee_pos} placeholder="Должность" />
      </div>
    </div>
    
    <div class="border-t border-gray-200 pt-4 mt-4">
      <h3 class="text-lg font-semibold mb-4">Алкогольные товары</h3>
      
      {#each form.products as product, index}
        <div class="card mb-4">
          <div class="grid grid-cols-6 gap-4 mb-4">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Товар {index + 1}</label>
              <input type="text" class="input" bind:value={product.name} placeholder="Название товара" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Количество</label>
              <input type="number" class="input" bind:value={product.kolvo} min="0.01" step="0.01" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Цена</label>
              <input type="number" class="input" bind:value={product.price} min="0" step="0.01" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">GTIN</label>
              <input type="text" class="input" bind:value={product.GTIN} placeholder="GTIN код" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Алкокод</label>
              <input type="text" class="input" bind:value={product.alc_code} placeholder="Алкокод" />
            </div>
            <div class="flex items-end">
              <button
                type="button"
                class="btn btn-danger w-full"
                on:click={() => removeProduct(index)}
              >
                ×
              </button>
            </div>
          </div>
          
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">QR код маркировки</label>
              <input type="text" class="input" bind:value={product.qr} placeholder="QR код маркировки" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Код марки ЕГАИС</label>
              <input type="text" class="input" bind:value={product.egais_mark_code} placeholder="Код марки для ЕГАИС" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">ID ЕГАИС</label>
              <input type="text" class="input" bind:value={product.egais_id} placeholder="Идентификатор ЕГАИС" />
            </div>
          </div>
        </div>
      {/each}
      
      <button type="button" class="btn btn-secondary mb-4" on:click={addProduct}>
        Добавить алкогольный товар
      </button>
    </div>
    
    <div class="flex gap-3 pt-4 border-t border-gray-200">
      <button type="submit" class="btn btn-primary" disabled={loading}>
        {loading ? 'Отправка...' : 'Отправить в ЕГАИС'}
      </button>
      <button type="button" class="btn btn-secondary" on:click={resetForm}>
        Сбросить
      </button>
    </div>
  </form>
</div>

