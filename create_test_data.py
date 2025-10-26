"""
Модуль для создания тестовых данных
Запускается только если установлена переменная окружения INIT_TEST_DATA=true
"""

import os
from loguru import logger
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(
        schemes=["pbkdf2_sha512"],
        deprecated="auto",
        pbkdf2_sha512__rounds=29000
    )
    return pwd_context.hash(password)

# Импортируем модели из api.models (после определения функций)
def _import_models():
    """Импорт моделей из api.models"""
    from api.models import Category, Product, User, Area, Seat
    return Category, Product, User, Area, Seat

async def create_test_data():
    """Создать все тестовые данные"""
    try:
        logger.info("Начинаем создание тестовых данных...")
        
        # Импортируем модели
        Category, Product, User, Area, Seat = _import_models()
        
        await create_default_categories(Category)
        await create_sample_products(Category, Product)
        await create_default_user(User)
        await create_default_areas_and_seats(Area, Seat)
        
        logger.success("Тестовые данные успешно созданы!")
        
    except Exception as e:
        logger.error(f"Ошибка создания тестовых данных: {e}")

async def create_default_categories(Category):
    """Создать базовые категории товаров"""
    try:
        count = await Category.all().count()
        if count > 0:
            logger.info(f"Категории уже существуют: {count}")
            return
        
        categories = [
            {'name': 'Напитки', 'description': 'Безалкогольные и алкогольные напитки'},
            {'name': 'Закуски', 'description': 'Холодные и горячие закуски'},
            {'name': 'Основные блюда', 'description': 'Горячие основные блюда'},
            {'name': 'Десерты', 'description': 'Сладкие блюда и десерты'},
            {'name': 'Алкоголь', 'description': 'Алкогольные напитки'},
            {'name': 'Пиво', 'description': 'Пивные напитки'}
        ]
        
        for cat_data in categories:
            category = await Category.create(**cat_data)
            logger.info(f"Создана категория: {category.name}")
        
    except Exception as e:
        logger.error(f"Ошибка создания категорий: {e}")

async def create_sample_products(Category, Product):
    """Создать примеры товаров"""
    try:
        # Проверяем, есть ли уже товары
        count = await Product.all().count()
        if count > 0:
            logger.info(f"Товары уже существуют: {count}")
            return
        
        categories = {}
        for cat in await Category.all():
            categories[cat.name] = cat
        
        products = [
            {'name': 'Кока-кола 0.33л', 'description': 'Газированный напиток', 'category': 'Напитки', 
             'price': 120.0, 'barcode': '4607050690012', 'article': 'COCA_033'},
            {'name': 'Сок яблочный 0.2л', 'description': 'Натуральный яблочный сок', 'category': 'Напитки', 
             'price': 80.0, 'barcode': '4607050690029', 'article': 'JUICE_APPLE'},
            
            {'name': 'Картофель фри', 'description': 'Жареный картофель фри', 'category': 'Закуски', 
             'price': 180.0, 'article': 'FRIES_001'},
            {'name': 'Куриные крылышки', 'description': 'Острые куриные крылышки', 'category': 'Закуски', 
             'price': 320.0, 'article': 'WINGS_001'},
            
            {'name': 'Водка Premium 0.5л', 'description': 'Премиальная водка', 'category': 'Алкоголь', 
             'price': 1200.0, 'barcode': '4607001234567', 'article': 'VODKA_PREM', 
             'is_alcohol': True, 'is_marked': True, 'is_bottled': True, 'max_discount': 0},
            {'name': 'Пиво светлое 0.5л', 'description': 'Светлое пиво разливное', 'category': 'Пиво', 
             'price': 180.0, 'barcode': '4607001234574', 'article': 'BEER_LIGHT', 'unit': 'л',
             'is_alcohol': True, 'is_draught': True}
        ]
        
        for prod_data in products:
            category_name = prod_data.pop('category')
            category = categories.get(category_name)
            if category:
                prod_data['category'] = category
                product = await Product.create(**prod_data)
                logger.info(f"Создан товар: {product.name}")
                
    except Exception as e:
        logger.error(f"Ошибка создания товаров: {e}")

async def create_default_user(User):
    """Создать тестового пользователя"""
    try:
        count = await User.all().count()
        if count > 0:
            logger.info(f"Пользователи уже существуют: {count}")
            return
        
        user = await User.create(
            username="admin",
            password_hash=get_password_hash("admin"),
            is_active=True
        )
        logger.info(f"Создан пользователь: {user.username}")
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")

async def create_default_areas_and_seats(Area, Seat):
    """Создать тестовые области и места"""
    try:
        count = await Area.all().count()
        if count > 0:
            logger.info(f"Области уже существуют: {count}")
            return
        
        areas_data = [
            {'name': 'Основной зал', 'description': 'Главный зал ресторана', 'capacity': 50},
            {'name': 'VIP зал', 'description': 'VIP комната', 'capacity': 12},
            {'name': 'Летняя терраса', 'description': 'Открытая терраса', 'capacity': 30},
            {'name': 'Парк под деревом', 'description': 'Место для отдыха на свежем воздухе', 'capacity': 20},
        ]
        
        areas = {}
        for area_data in areas_data:
            area = await Area.create(**area_data)
            areas[area.name] = area
            logger.info(f"Создана область: {area.name}")
        
        seats_config = [
            {'area': 'Основной зал', 'seats': [
                {'number': '1', 'capacity': 4},
                {'number': '2', 'capacity': 2},
                {'number': '3', 'capacity': 4},
                {'number': '4', 'capacity': 6},
                {'number': '5', 'capacity': 2},
                {'number': '6', 'capacity': 4},
                {'number': '7', 'capacity': 4},
                {'number': '8', 'capacity': 8},
                {'number': '9', 'capacity': 2},
                {'number': '10', 'capacity': 4},
            ]},
            {'area': 'VIP зал', 'seats': [
                {'number': '1', 'capacity': 4},
                {'number': '2', 'capacity': 4},
                {'number': '3', 'capacity': 6},
                {'number': '4', 'capacity': 4},
            ]},
            {'area': 'Летняя терраса', 'seats': [
                {'number': '1', 'capacity': 2},
                {'number': '2', 'capacity': 2},
                {'number': '3', 'capacity': 4},
                {'number': '4', 'capacity': 4},
                {'number': '5', 'capacity': 2},
                {'number': '6', 'capacity': 4},
                {'number': '7', 'capacity': 4},
                {'number': '8', 'capacity': 6},
            ]},
            {'area': 'Парк под деревом', 'seats': [
                {'number': 'Дерево 1', 'capacity': 6, 'description': 'Большой стол под дубом'},
                {'number': 'Дерево 2', 'capacity': 4, 'description': 'Стол под липой'},
                {'number': 'Дерево 3', 'capacity': 2, 'description': 'Маленький стол под кленом'},
                {'number': 'Дерево 4', 'capacity': 4, 'description': 'Стол под березой'},
                {'number': 'Дерево 5', 'capacity': 4, 'description': 'Стол под ивой'},
            ]},
        ]
        
        for config in seats_config:
            area = areas.get(config['area'])
            if area:
                for seat_data in config['seats']:
                    seat = await Seat.create(area=area, **seat_data)
                    logger.info(f"Создано место: {area.name} - {seat.number}")
                    
    except Exception as e:
        logger.error(f"Ошибка создания областей и мест: {e}")
