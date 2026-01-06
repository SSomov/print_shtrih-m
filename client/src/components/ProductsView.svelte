<script>
import { onMount } from "svelte";
import api from "../lib/api.js";

let loading = false;
let categories = [];
let products = [];
let selectedCategory = null;
let pagination = {
	page: 1,
	limit: 20,
	total: 0,
};

let showCategoryForm = false;
let showProductForm = false;
let editingCategory = null;
let editingProduct = null;

let categoryForm = {
	name: "",
	description: "",
	parent_id: null,
};

let productForm = {
	name: "",
	description: "",
	category_id: null,
	price: 0,
	barcode: "",
	legacy_path: "",
	unit: "шт",
	max_discount: 100,
	tax_rate: 20,
	is_alcohol: false,
	is_marked: false,
	is_draught: false,
	is_bottled: false,
	alc_code: "",
	egais_mark_code: "",
	gtin: "",
};

$: categoriesTree = buildTree(categories);
$: flatCategories = flattenCategories(categoriesTree);

function buildTree(cats, parentId = null) {
	return cats
		.filter(
			(cat) =>
				(cat.parent_id === null && parentId === null) ||
				cat.parent_id === parentId
		)
		.map((cat) => ({
			id: cat.id,
			name: cat.name,
			description: cat.description,
			parent_id: cat.parent_id,
			children: buildTree(cats, cat.id),
		}));
}

function flattenCategories(tree, level = 0) {
	let result = [];
	for (const cat of tree) {
		result.push({
			...cat,
			level: level,
			displayName: "  ".repeat(level) + cat.name,
		});
		if (cat.children && cat.children.length > 0) {
			result = result.concat(flattenCategories(cat.children, level + 1));
		}
	}
	return result;
}

onMount(async () => {
	await loadCategories();
	await loadProducts();
});

async function refresh() {
	await Promise.all([loadCategories(), loadProducts()]);
}

async function loadCategories() {
	try {
		const response = await api.get("/categories");
		if (response.data.status === "success") {
			categories = response.data.data;
		}
	} catch (error) {
		console.error("Ошибка загрузки категорий:", error);
	}
}

async function loadProducts() {
	loading = true;
	try {
		const params = {
			page: pagination.page,
			limit: pagination.limit,
		};

		if (selectedCategory) {
			params.category_id = selectedCategory.id;
		}

		const response = await api.get("/products", { params });
		if (response.data.status === "success") {
			products = response.data.data;
			pagination = response.data.pagination;
		}
	} catch (error) {
		console.error("Ошибка загрузки товаров:", error);
	} finally {
		loading = false;
	}
}

function selectCategory(category) {
	selectedCategory = category;
	pagination.page = 1;
	loadProducts();
}

function addCategory() {
	editingCategory = null;
	categoryForm = { name: "", description: "", parent_id: null };
	showCategoryForm = true;
}

function editCategory(category) {
	editingCategory = category;
	categoryForm = {
		name: category.name,
		description: category.description || "",
		parent_id: category.parent_id || 0,
	};
	showCategoryForm = true;
}

async function saveCategory() {
	try {
		const formData = new FormData();
		formData.append("name", categoryForm.name);
		if (categoryForm.description) {
			formData.append("description", categoryForm.description);
		}

		if (
			categoryForm.parent_id !== null &&
			categoryForm.parent_id !== undefined &&
			categoryForm.parent_id !== 0
		) {
			formData.append("parent_id", categoryForm.parent_id.toString());
		}

		if (editingCategory) {
			await api.put(`/categories/${editingCategory.id}`, formData);
		} else {
			await api.post("/categories", formData);
		}

		showCategoryForm = false;
		editingCategory = null;
		categoryForm = { name: "", description: "", parent_id: null };
		await loadCategories();
	} catch (error) {
		alert("Ошибка сохранения категории: " + error.message);
	}
}

async function deleteCategory(category) {
	if (!confirm(`Удалить категорию "${category.name}"?`)) return;

	try {
		await api.delete(`/categories/${category.id}`);
		await loadCategories();

		if (selectedCategory && selectedCategory.id === category.id) {
			selectedCategory = null;
			await loadProducts();
		}
	} catch (error) {
		alert("Ошибка удаления категории: " + error.message);
	}
}

function addProduct() {
	editingProduct = null;
	resetProductForm();
	showProductForm = true;
}

function editProduct(product) {
	editingProduct = product;
	productForm = { ...product };
	productForm.category_id = product.category.id;
	showProductForm = true;
}

async function saveProduct() {
	try {
		if (editingProduct) {
			await api.put(`/products/${editingProduct.id}`, productForm);
		} else {
			await api.post("/products", productForm);
		}

		showProductForm = false;
		editingProduct = null;
		resetProductForm();
		await loadProducts();
	} catch (error) {
		alert("Ошибка сохранения товара: " + error.message);
	}
}

async function deleteProduct(product) {
	if (!confirm(`Удалить товар "${product.name}"?`)) return;

	try {
		await api.delete(`/products/${product.id}`);
		await loadProducts();
	} catch (error) {
		alert("Ошибка удаления товара: " + error.message);
	}
}

function resetProductForm() {
	productForm = {
		name: "",
		description: "",
		category_id: selectedCategory ? selectedCategory.id : null,
		price: 0,
		barcode: "",
		legacy_path: "",
		unit: "шт",
		max_discount: 100,
		tax_rate: 20,
		is_alcohol: false,
		is_marked: false,
		is_draught: false,
		is_bottled: false,
		alc_code: "",
		egais_mark_code: "",
		gtin: "",
	};
}

function handleSizeChange(val) {
	pagination.limit = val;
	pagination.page = 1;
	loadProducts();
}

function handleCurrentChange(val) {
	pagination.page = val;
	loadProducts();
}
</script>

<div class="grid grid-cols-6 gap-4">
  <!-- Категории -->
  <div class="col-span-2">
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Категории</h3>
        <button class="btn btn-primary text-sm" on:click={addCategory}>
          + Добавить
        </button>
      </div>
      
      <div class="space-y-1 max-h-96 overflow-y-auto">
        {#each categoriesTree as category}
          <div class="p-2 hover:bg-gray-100 rounded cursor-pointer {selectedCategory?.id === category.id ? 'bg-primary-50' : ''}"
               on:click={() => selectCategory(category)}>
            <div class="flex justify-between items-center">
              <span>{category.name}</span>
              <div class="flex gap-1">
                <button class="text-primary-500 hover:text-primary-700" on:click|stopPropagation={() => editCategory(category)}>
                  ✏️
                </button>
                <button class="text-danger-500 hover:text-danger-700" on:click|stopPropagation={() => deleteCategory(category)}>
                  🗑️
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Товары -->
  <div class="col-span-4">
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">Товары</h3>
        <div class="flex gap-2">
          <button class="btn btn-secondary text-sm" on:click={refresh}>Обновить</button>
          <button class="btn btn-primary text-sm" on:click={addProduct}>+ Добавить товар</button>
        </div>
      </div>

      {#if loading}
        <div class="text-center py-8">Загрузка...</div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead>
              <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2 text-left">Название</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Цена</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Штрихкод</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Ед. изм.</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Особенности</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Макс. скидка</th>
                <th class="border border-gray-300 px-4 py-2 text-left">Действия</th>
              </tr>
            </thead>
            <tbody>
              {#each products as product}
                <tr class="hover:bg-gray-50">
                  <td class="border border-gray-300 px-4 py-2">{product.name}</td>
                  <td class="border border-gray-300 px-4 py-2">{product.price} Р</td>
                  <td class="border border-gray-300 px-4 py-2">{product.barcode || '-'}</td>
                  <td class="border border-gray-300 px-4 py-2">{product.unit}</td>
                  <td class="border border-gray-300 px-4 py-2">
                    <div class="flex gap-1">
                      {#if product.is_alcohol}
                        <span class="px-2 py-1 bg-warning-100 text-warning-700 rounded text-xs">Алко</span>
                      {/if}
                      {#if product.is_marked}
                        <span class="px-2 py-1 bg-danger-100 text-danger-700 rounded text-xs">Марк.</span>
                      {/if}
                      {#if product.is_draught}
                        <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">Разл.</span>
                      {/if}
                    </div>
                  </td>
                  <td class="border border-gray-300 px-4 py-2">{product.max_discount}%</td>
                  <td class="border border-gray-300 px-4 py-2">
                    <div class="flex gap-2">
                      <button class="text-primary-500 hover:text-primary-700" on:click={() => editProduct(product)}>✏️</button>
                      <button class="text-danger-500 hover:text-danger-700" on:click={() => deleteProduct(product)}>🗑️</button>
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>

        {#if pagination.total > 0}
          <div class="flex justify-between items-center mt-4">
            <div class="text-sm text-gray-600">
              Показано {((pagination.page - 1) * pagination.limit) + 1} - {Math.min(pagination.page * pagination.limit, pagination.total)} из {pagination.total}
            </div>
            <div class="flex gap-2">
              <button
                class="btn btn-secondary text-sm"
                disabled={pagination.page === 1}
                on:click={() => handleCurrentChange(pagination.page - 1)}
              >
                Назад
              </button>
              <button
                class="btn btn-secondary text-sm"
                disabled={pagination.page * pagination.limit >= pagination.total}
                on:click={() => handleCurrentChange(pagination.page + 1)}
              >
                Вперед
              </button>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>

<!-- Диалог категории -->
{#if showCategoryForm}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="card w-full max-w-md">
      <h3 class="text-lg font-semibold mb-4">{editingCategory ? 'Редактировать категорию' : 'Новая категория'}</h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
          <input type="text" class="input" bind:value={categoryForm.name} placeholder="Введите название категории" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Родительская категория</label>
          <select class="input" bind:value={categoryForm.parent_id}>
            <option value={0}>Корневая категория</option>
            {#each flatCategories as cat}
              <option value={cat.id} disabled={editingCategory && cat.id === editingCategory.id}>
                {cat.displayName}
              </option>
            {/each}
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
          <textarea class="input" rows="3" bind:value={categoryForm.description} placeholder="Введите описание категории"></textarea>
        </div>
      </div>
      
      <div class="flex gap-3 mt-6">
        <button class="btn btn-secondary flex-1" on:click={() => showCategoryForm = false}>Отмена</button>
        <button class="btn btn-primary flex-1" on:click={saveCategory}>Сохранить</button>
      </div>
    </div>
  </div>
{/if}

<!-- Диалог товара -->
{#if showProductForm}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto p-4">
    <div class="card w-full max-w-4xl my-8">
      <h3 class="text-lg font-semibold mb-4">{editingProduct ? 'Редактировать товар' : 'Новый товар'}</h3>
      
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
          <input type="text" class="input" bind:value={productForm.name} placeholder="Название товара" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Категория *</label>
          <select class="input" bind:value={productForm.category_id}>
            <option value={null}>Выберите категорию</option>
            {#each flatCategories as cat}
              <option value={cat.id}>{cat.displayName}</option>
            {/each}
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Цена *</label>
          <input type="number" class="input" bind:value={productForm.price} min="0" step="0.01" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Штрихкод</label>
          <input type="text" class="input" bind:value={productForm.barcode} placeholder="EAN код" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Legacy Path</label>
          <input type="text" class="input" bind:value={productForm.legacy_path} placeholder="Путь из старой системы" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Единица измерения</label>
          <input type="text" class="input" bind:value={productForm.unit} placeholder="шт" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Макс. скидка (%)</label>
          <input type="number" class="input" bind:value={productForm.max_discount} min="0" max="100" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">НДС (%)</label>
          <input type="number" class="input" bind:value={productForm.tax_rate} min="0" max="100" />
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
          <textarea class="input" rows="3" bind:value={productForm.description} placeholder="Описание товара"></textarea>
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-2">Особенности</label>
          <div class="space-y-2">
            <label class="flex items-center gap-2">
              <input type="checkbox" bind:checked={productForm.is_alcohol} />
              <span>Алкогольный товар</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" bind:checked={productForm.is_marked} />
              <span>Маркированный товар</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" bind:checked={productForm.is_draught} disabled={!productForm.is_alcohol} />
              <span>Разливное</span>
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" bind:checked={productForm.is_bottled} disabled={!productForm.is_alcohol} />
              <span>Бутылочное</span>
            </label>
          </div>
        </div>
        
        {#if productForm.is_alcohol}
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Алкокод</label>
            <input type="text" class="input" bind:value={productForm.alc_code} placeholder="Код алкогольной продукции" />
          </div>
          {#if productForm.is_marked}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">GTIN</label>
              <input type="text" class="input" bind:value={productForm.gtin} placeholder="GTIN для маркированных товаров" />
            </div>
          {/if}
        {/if}
      </div>
      
      <div class="flex gap-3 mt-6">
        <button class="btn btn-secondary flex-1" on:click={() => showProductForm = false}>Отмена</button>
        <button class="btn btn-primary flex-1" on:click={saveProduct}>Сохранить</button>
      </div>
    </div>
  </div>
{/if}

