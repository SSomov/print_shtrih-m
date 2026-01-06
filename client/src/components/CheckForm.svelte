<script>
import { checkApi } from "../lib/api.js";

let loading = false;
let paymentType = "cash";
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
			mark: "0",
			GTIN: "",
			qr: "",
			alc_code: "",
			egais_mark_code: "",
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
			mark: "0",
			GTIN: "",
			qr: "",
			alc_code: "",
			egais_mark_code: "",
		},
	];
}

function removeProduct(index) {
	if (form.products.length > 1) {
		form.products = form.products.filter((_, i) => i !== index);
	}
}

async function submitCheck() {
	loading = true;
	try {
		let result;
		if (paymentType === "cash") {
			result = await checkApi.cashPayment(form);
		} else {
			result = await checkApi.cardPayment(form);
		}

		if (result.data.status === "success") {
			alert("Чек успешно пробит!");
			resetForm();
		} else {
			alert("Ошибка: " + result.data.message);
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
				mark: "0",
				GTIN: "",
				qr: "",
				alc_code: "",
				egais_mark_code: "",
			},
		],
	};
}
</script>

<div class="card">
  <h2 class="card-header">Пробитие чека</h2>
  
  <form on:submit|preventDefault={submitCheck} class="space-y-4">
    <div class="grid grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Номер заказа</label>
        <input type="text" class="input" bind:value={form.num} placeholder="Введите номер заказа" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Тип документа</label>
        <select class="input" bind:value={form.typedoc}>
          <option value="check">Чек</option>
          <option value="return">Возврат</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Тип оплаты</label>
        <select class="input" bind:value={paymentType}>
          <option value="cash">Наличные</option>
          <option value="card">Карта</option>
        </select>
      </div>
    </div>
    
    <div class="grid grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Зал</label>
        <input type="text" class="input" bind:value={form.hall} placeholder="Номер зала" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Стол</label>
        <input type="text" class="input" bind:value={form.table} placeholder="Номер стола" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Официант</label>
        <input type="text" class="input" bind:value={form.waiter} placeholder="Имя официанта" />
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Сотрудник ФИО</label>
        <input type="text" class="input" bind:value={form.employee_fio} placeholder="ФИО сотрудника" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ИНН сотрудника</label>
        <input type="text" class="input" bind:value={form.employee_inn} placeholder="ИНН сотрудника" />
      </div>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Должность</label>
        <input type="text" class="input" bind:value={form.employee_pos} placeholder="Должность" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Общая скидка %</label>
        <input type="number" class="input" bind:value={form.alldiscount} min="0" max="100" />
      </div>
    </div>
    
    <div class="border-t border-gray-200 pt-4 mt-4">
      <h3 class="text-lg font-semibold mb-4">Товары</h3>
      
      {#each form.products as product, index}
        <div class="card mb-4">
          <div class="grid grid-cols-5 gap-4 mb-4">
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
            <div class="flex items-end">
              <button
                type="button"
                class="btn btn-danger w-full"
                on:click={() => removeProduct(index)}
              >
                Удалить
              </button>
            </div>
          </div>
          
          <div class="flex items-center gap-2 mb-4">
            <input
              type="checkbox"
              id="mark-{index}"
              checked={product.mark === '1' || product.mark === true}
              on:change={(e) => product.mark = e.target.checked ? '1' : '0'}
              class="w-4 h-4"
            />
            <label for="mark-{index}" class="text-sm font-medium text-gray-700">Маркировка</label>
          </div>
          
          {#if product.mark === '1' || product.mark === true}
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">GTIN</label>
                <input type="text" class="input" bind:value={product.GTIN} placeholder="GTIN код" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">QR код</label>
                <input type="text" class="input" bind:value={product.qr} placeholder="QR код маркировки" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Алкокод</label>
                <input type="text" class="input" bind:value={product.alc_code} placeholder="Алкокод для ЕГАИС" />
              </div>
            </div>
          {/if}
        </div>
      {/each}
      
      <button type="button" class="btn btn-secondary mb-4" on:click={addProduct}>
        Добавить товар
      </button>
    </div>
    
    <div class="flex gap-3 pt-4 border-t border-gray-200">
      <button type="submit" class="btn btn-primary" disabled={loading}>
        {loading ? 'Обработка...' : 'Пробить чек'}
      </button>
      <button type="button" class="btn btn-secondary" on:click={resetForm}>
        Сбросить
      </button>
    </div>
  </form>
</div>

