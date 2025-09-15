from typing import Union, List

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

from escpos.printer import Network

from datetime import datetime
import win32com.client
import argparse
import json

from dotenv import load_dotenv
import os
import requests
from lxml import etree
import xml.etree.ElementTree as ET
import time
import traceback

from tortoise import Tortoise
from tortoise.models import Model
from tortoise import fields

load_dotenv()

# Глобальные переменные для кэширования данных ККТ
KKT_CACHE = {
    'INN': None,
    'KKTRegistrationNumber': None,
    'KKTSerialNumber': None,
    'FNSerialNumber': None,
    'initialized': False
}

# Модели для Tortoise ORM
class CheckLog(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=20)
    message = fields.TextField(null=True)
    error = fields.TextField(null=True)
    order_data = fields.JSONField(null=True)
    result_code = fields.CharField(max_length=10, null=True)
    result_description = fields.TextField(null=True)
    filename = fields.CharField(max_length=255, null=True)
    document_number = fields.CharField(max_length=50, null=True)  # Номер чека
    fiscal_sign = fields.CharField(max_length=50, null=True)  # Фискальный признак

    class Meta:
        table = "check_logs"

class EgaisLog(Model):
    id = fields.IntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    order_data = fields.JSONField(null=True)
    xml_data = fields.TextField(null=True)
    response_data = fields.TextField(null=True)
    qr_code = fields.TextField(null=True)
    status = fields.CharField(max_length=20)
    error = fields.TextField(null=True)
    xml_file = fields.CharField(max_length=255, null=True)
    saved_file = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "egais_logs"

# Инициализация Tortoise ORM
async def init_db():
    try:
        await Tortoise.init(
            db_url=f"postgres://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'print_logs')}",
            modules={'models': ['srv']}
        )
        await Tortoise.generate_schemas()
        print("PostgreSQL подключен успешно")
        return True
    except Exception as e:
        print(f"Ошибка подключения к PostgreSQL: {e}")
        print("Будет использоваться файловое логирование")
        return False

class Item(BaseModel):
    description: str = None
    pos: str = None
    product: str = None
    mod: str = None
    mark: str = None
    qr: str = None
    draught: str = None
    bottled: str = None
    maxdiscont: str = None
    GTIN: str = None
    name: str = None
    kolvo: str = None
    price: str = None
    totalnodiscount: str = None
    discount: str = None
    sdiscount: str = None
    total: str = None
    # ЕГАИС поля
    alc_code: str = None  # Алкокод продукции
    egais_mark_code: str = None  # Код марки для ЕГАИС
    egais_id: str = None  # Идентификатор ЕГАИС

class Order(BaseModel):
    num: str = None
    typedoc: str = None

    hall: str = None
    table: str = None
    create: str = None
    fdiscount: str = None
    sdiscount: str = None
    pdiscount: str = None
    alldiscount: str = None
    waiter: str = None 
    employee_fio: str = None
    employee_pos: str = None
    employee_inn: str = None
    products: List[Item] = None

class Employee(BaseModel):
    fio: str = None
    pos: str = None
    inn: str = None

class KitchenMarkRequest(BaseModel):
    printer_ip: str
    table_number: int
    waiter_name: str
    order_number: int
    kitchen_type: str
    products: List[Item] = None

app = FastAPI()

# Инициализация БД при запуске
db_connected = False

@app.on_event("startup")
async def startup_event():
    global db_connected
    db_connected = await init_db()
    
    # Инициализируем кэш данных ККТ
    initialize_kkt_cache()

def add_spaces_to_45_chars(input_string): 
    total_spaces = 45 - len(input_string)
    left_spaces = total_spaces // 2
    right_spaces = total_spaces - left_spaces
    # Добавляем пробелы слева и справа
    padded_string = " " * left_spaces + input_string + " " * right_spaces
    return padded_string

def get_ecr_mode(fr: win32com.client.CDispatch):
    """
    Функция запроса режима кассы.
    
    :param fr: объект драйвера кассы (CDispatch)
    :return: Кортеж (int, str) — режим кассы и его описание
    """
    fr.Password = 30
    fr.GetECRStatus()
    return fr.ECRMode, fr.ECRModeDescription

def send_tag_1021_1203(fr, fio, inn) -> None:
    """
    функция отправки тэгов 1021 и 1203
    ФИО кассира и ИНН кассира
    :param comp_rec: dict словарь нашего чека
    :return:
    """
    fr.TagNumber = 1021
    fr.TagType = 7
    fr.TagValueStr = fio
    fr.FNSendTag()
    fr.TagNumber = 1203
    fr.TagType = 7
    fr.TagValueStr = inn
    fr.FNSendTag()

def send_user_details(fr, numdoc) -> None:
    """
    функция отправки тэгов 1260 -> 1262, 1263, 1264, 1265
    :param fr: объект драйвера
    :param numdoc: номер документа
    :return:
    """
    tags = [
        (1262, "030"),
        (1263, datetime.now().strftime("%d.%m.%Y")),
        (1264, numdoc),
        (1265, "mode=horeca")
    ] 
    for tag_number, tag_value in tags:
        fr.TagNumber = tag_number
        fr.TagType = 7
        fr.TagValueStr = tag_value
        fr.FNSendTagOperation()
    print(fr.ResultCode, fr.ResultCodeDescription)
    """
        Значение реквизита «отраслевой реквизит предмета расчета» 1260
        Значение реквизита «идентификатор ФОИВ» (тег 1262): 030
        Значение реквизита «дата документа основания» (тег 1263): 26.03.2022
        Значение реквизита «номер документа основания» (тег 1264): 477
        Значение реквизита «значение отраслевого реквизита» (тег 1265): mode=horeca
    """

def save_check_result_file(prefix, content, error=None):
    """
    Сохранить результат чека в файл (резервный способ)
    """
    import os
    
    # Создаем папку check если её нет
    check_dir = "check"
    if not os.path.exists(check_dir):
        os.makedirs(check_dir)
    
    ts = time.strftime('%Y%m%d_%H%M%S')
    filename = f"{prefix}_{ts}.txt"
    filepath = os.path.join(check_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"=== {prefix.upper()} ===\n")
        if error:
            f.write(f"[ERROR]\n{error}\n")
        f.write(content)
    return filepath

async def save_check_result(status, message, error=None, order_data=None, result_code=None, result_description=None, document_number=None, fiscal_sign=None):
    """
    Сохранить результат чека в БД, при ошибке - в файл
    """
    global db_connected
    if not db_connected:
        # Если БД не подключена, сразу сохраняем в файл
        content = f"Status: {status}\nMessage: {message}\n"
        if error:
            content += f"Error: {error}\n"
        if order_data:
            content += f"Order: {order_data}\n"
        if result_code:
            content += f"ResultCode: {result_code}\n"
        if result_description:
            content += f"ResultDescription: {result_description}\n"
        if document_number:
            content += f"DocumentNumber: {document_number}\n"
        if fiscal_sign:
            content += f"FiscalSign: {fiscal_sign}\n"
        save_check_result_file("check", content, error)
        return False
    
    try:
        await CheckLog.create(
            status=status,
            message=message,
            error=error,
            order_data=order_data,
            result_code=result_code,
            result_description=result_description,
            document_number=document_number,
            fiscal_sign=fiscal_sign
        )
        return True
    except Exception as e:
        print(f"Ошибка сохранения в БД: {e}, сохраняем в файл")
        # Резервное сохранение в файл
        content = f"Status: {status}\nMessage: {message}\n"
        if error:
            content += f"Error: {error}\n"
        if order_data:
            content += f"Order: {order_data}\n"
        if result_code:
            content += f"ResultCode: {result_code}\n"
        if result_description:
            content += f"ResultDescription: {result_description}\n"
        if document_number:
            content += f"DocumentNumber: {document_number}\n"
        if fiscal_sign:
            content += f"FiscalSign: {fiscal_sign}\n"
        save_check_result_file("check", content, error)
        return False

async def save_egais_result(status, order_data=None, xml_data=None, response_data=None, qr_code=None, error=None, xml_file=None, saved_file=None):
    """
    Сохранить результат ЕГАИС в БД, при ошибке - в файл
    """
    global db_connected
    if not db_connected:
        # Если БД не подключена, сразу сохраняем в файл
        content = f"Status: {status}\n"
        if order_data:
            content += f"Order: {order_data}\n"
        if xml_data:
            content += f"XML: {xml_data}\n"
        if response_data:
            content += f"Response: {response_data}\n"
        if qr_code:
            content += f"QR Code: {qr_code}\n"
        if error:
            content += f"Error: {error}\n"
        save_check_result_file("egais", content, error)
        return False
    
    try:
        await EgaisLog.create(
            status=status,
            order_data=order_data,
            xml_data=xml_data,
            response_data=response_data,
            qr_code=qr_code,
            error=error,
            xml_file=xml_file,
            saved_file=saved_file
        )
        return True
    except Exception as e:
        print(f"Ошибка сохранения в БД: {e}, сохраняем в файл")
        # Резервное сохранение в файл
        content = f"Status: {status}\n"
        if order_data:
            content += f"Order: {order_data}\n"
        if xml_data:
            content += f"XML: {xml_data}\n"
        if response_data:
            content += f"Response: {response_data}\n"
        if qr_code:
            content += f"QR Code: {qr_code}\n"
        if error:
            content += f"Error: {error}\n"
        save_check_result_file("egais", content, error)
        return False

async def order_pay(order, type_pay):
    try:
        print(order)
        max_discount = os.getenv('MAX_DISCOUNT', 'False') in ['True']
        discount = 0
        total_to_pay = 0
        item_no_discount = False
        if float(order.alldiscount) > 0 and float(order.alldiscount) <= 100:
            discount = float(order.alldiscount) / 100    
        fr = win32com.client.Dispatch('Addin.DRvFR')
        fr.Connect()
        ecr_mode, ecr_description = get_ecr_mode(fr)
        print(f"ECR Mode: {ecr_mode}, Description: {ecr_description}")
        fr.Summ1Enabled = False
        fr.TaxValueEnabled = False
        for item in order.products:
            quantity = float(item.kolvo)
            item_discount = discount
            if max_discount:
                item_discount = min(discount, float(item.maxdiscont) / 100)
                item_no_discount = True
            price = float(item.price)*(1 - item_discount)
            print(quantity,price)
            measure_unit = 0
            PaymentItemSign = 1
            print(item)
            if item.mark == '1' and item.draught == '1':
                print("алко разливное пиво")
                fr.DivisionalQuantity = False
                fr.Numerator = "1";
                fr.Denominator = "1";
                measure_unit = 41
                PaymentItemSign = 31
            elif item.mark == '1' and item.bottled == '1':
                print("алко пиво")
                PaymentItemSign = 31
            elif item.mark == '1':
                print("иные маркированные")
                PaymentItemSign = 33
            fr.MeasureUnit = measure_unit
            fr.StringForPrinting = item.name
            fr.Price = price
            fr.Quantity = quantity
            fr.PaymentTypeSign = 4
            fr.PaymentItemSign =  PaymentItemSign
            fr.FNOperation()
            print(fr.ResultCode, fr.ResultCodeDescription)
            total_to_pay += float(item.kolvo) * float(item.price) * (1 - item_discount)
            if item.mark == '1' and item.draught == '1':
                send_user_details(fr, order.num.strip())
                fr.MCOSUSign = True
                fr.Barcode = item.GTIN
                fr.FNSendItemBarcode()
                print(fr.MarkingTypeEx, fr.MarkingType, fr.CheckItemLocalResult)
                print(fr.ResultCode, fr.ResultCodeDescription)
            elif item.mark == '1':
                qr_add_gs = item.qr.replace('{GS}', chr(29))
                fr.BarCode = qr_add_gs
                fr.ItemStatus = 1
                fr.FNCheckItemBarcode()
                fr.FNAcceptMarkingCode()
                print(fr.MarkingTypeEx, fr.MarkingType, fr.CheckItemLocalResult)
                print(fr.ResultCode, fr.ResultCodeDescription)
                fr.Barcode = qr_add_gs
                fr.FNSendItemBarcode()
        if float(order.alldiscount) > 0 and float(order.alldiscount) <= 100:
            summ_no_discount = sum(float(item.kolvo) * float(item.price) for item in order.products)
            fr.StringQuantity = 1
            fr.FeedDocument()
            fr.StringForPrinting = f"Скидка .. {order.alldiscount}%"
            fr.PrintString()
            if item_no_discount:
                fr.StringForPrinting = f"В чеке присутствуют товары скидка на которые не распространяется!"
                fr.PrintString()
            fr.StringForPrinting = f"Сумма чека без скидки .. {summ_no_discount}"
            fr.PrintString()
        if type_pay == "cash":
            fr.Summ1 = total_to_pay
        if type_pay == "card":
            fr.Summ2 = total_to_pay
        send_tag_1021_1203(fr, order.employee_pos + " " + order.employee_fio, order.employee_inn)
        fr.FNCloseCheckEx()
        print(fr.ResultCode, fr.ResultCodeDescription)
        fr.StringQuantity = 2
        fr.FeedDocument()
        fr.CutType = 2
        fr.CutCheck()
        
        # Получаем данные ККТ из кэша и актуальные данные чека
        check_info = None
        result_code = fr.ResultCode
        result_description = fr.ResultCodeDescription
        
        try:
            # Получаем параметры текущей смены
            fr.FNGetCurrentSessionParams()
            session_number = getattr(fr, 'SessionNumber', None)
            
            # Получаем текущее время в формате для ЕГАИС (DDMMYYHHMM)
            now = datetime.now()
            egais_datetime = now.strftime("%d%m%y%H%M")
            
            # Используем кэшированные данные для остальных параметров
            check_info = {
                'FDNumber': str(fr.DocumentNumber) if hasattr(fr, 'DocumentNumber') and fr.DocumentNumber else None,
                'FNSerialNumber': KKT_CACHE['FNSerialNumber'],
                'KKTNumber': KKT_CACHE['KKTSerialNumber'],
                'KKTRegistrationNumber': KKT_CACHE['KKTRegistrationNumber'],
                'FP': str(fr.FiscalSign) if hasattr(fr, 'FiscalSign') and fr.FiscalSign else None,
                'ShiftNumber': session_number,  # Номер смены
                'EgaisDateTime': egais_datetime  # Время в формате ЕГАИС
            }
            
            print(f"Используются кэшированные данные ККТ: {check_info}")
        except Exception as e:
            print(f"Ошибка получения данных ККТ: {e}")
        
        fr.Disconnect()
        
        # Сохраняем успешный чек в БД
        document_number = None
        fiscal_sign = None
        if check_info:
            document_number = check_info.get('FDNumber')
            fiscal_sign = check_info.get('FP')
        
        await save_check_result(
            status="success",
            message="Чек успешно напечатан",
            order_data=order.dict(),
            result_code=str(result_code),
            result_description=result_description,
            document_number=document_number,
            fiscal_sign=fiscal_sign
        )
        
        # Проверяем, есть ли алкогольные позиции для отправки в ЕГАИС
        alco_items = [item for item in order.products if item.mark == '1' or item.alc_code or item.egais_mark_code]
        if alco_items:
            try:
                # Если не удалось получить данные из ККТ, не отправляем в ЕГАИС
                if not check_info:
                    print("Не удалось получить данные ККТ, пропускаем отправку в ЕГАИС")
                    return {"status": "success", "message": "Чек успешно напечатан, но не отправлен в ЕГАИС"}
                
                egais_result = await send_egais_check(order, check_info)
                print(f"ЕГАИС результат: {egais_result}")
            except Exception as e:
                print(f"Ошибка отправки в ЕГАИС: {e}")
        return {"status": "success", "message": "Чек успешно напечатан"}
    except Exception as e:
        # Сохраняем ошибку в БД
        await save_check_result(
            status="error",
            message="Ошибка при печати чека",
            error=str(e),
            order_data=order.dict(),
            document_number=None,
            fiscal_sign=None
        )
        return {"status": "error", "message": "Ошибка при печати чека", "error": str(e)}

@app.post("/api/v1/invoice")
async def create_invoice(order: Order):
    print(order)
    max_discount = os.getenv('MAX_DISCOUNT', 'False') in ['True']
    cut_invoice = os.getenv('CUT_INVOICE', 'False') in ['True']
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    fr.UseReceiptRibbon = True
    fr.StringQuantity = 1
    fr.FeedDocument()
    fr.StringForPrinting = add_spaces_to_45_chars(os.getenv('ORG_TITLE', 'Кафе'))
    fr.PrintString()
    fr.StringQuantity = 1
    fr.FeedDocument()
    fr.StringForPrinting = f"    СЧЕТ #{order.num.strip()}"
    fr.PrintWideString()
    fr.StringQuantity = 1
    fr.FeedDocument()
    fr.StringForPrinting = f"ЗАЛ {order.hall.strip()}"
    fr.PrintString()
    fr.StringForPrinting = f"СТОЛ {order.table.strip()}"
    fr.PrintString()
    fr.StringForPrinting = f"Официант {order.waiter.strip()}"
    fr.PrintString()
    fr.StringForPrinting = f"Счет открыт {order.create.strip()}"
    fr.PrintString()
    fr.StringQuantity = 1
    fr.FeedDocument()
    fr.StringForPrinting = add_spaces_to_45_chars(f"Блюда")
    fr.PrintString()
    discount = 0
    total_to_pay = 0
    item_no_discount = False
    if float(order.alldiscount) > 0 and float(order.alldiscount) <= 100:
        discount = float(order.alldiscount) / 100
    for item in order.products:
        print(item)
        fr.StringForPrinting = f"{item.name.upper()}...{item.kolvo}x{item.price}  {float(item.kolvo)*float(item.price)}"
        fr.PrintString()
        fr.StringQuantity = 1
        fr.FeedDocument()
        item_discount = discount
        if max_discount:
            item_discount = min(discount, float(item.maxdiscont) / 100)
            item_no_discount = True
        total_to_pay += float(item.kolvo) * float(item.price) * (1 - item_discount)
    # Проверка условия, что скидка больше 0 и меньше или равна 100
    if float(order.alldiscount) > 0 and float(order.alldiscount) <= 100:
        summ_no_discount = sum(float(item.kolvo) * float(item.price) for item in order.products)
        fr.StringQuantity = 2
        fr.FeedDocument()
        fr.StringForPrinting = f"Скидка .. {order.alldiscount}%"
        fr.PrintString()
        if item_no_discount:
            fr.StringForPrinting = f"В чеке присутствуют товары скидка на которые не распространяется!"
            fr.PrintString()
        fr.StringForPrinting = f"Сумма чека без скидки .. {summ_no_discount}"
        fr.PrintString()
    fr.StringQuantity = 2
    fr.FeedDocument()
    fr.StringForPrinting = f"ИТОГО К ОПЛАТЕ .. {total_to_pay}"
    fr.PrintWideString()    
#    fr.StringQuantity = 2
#    fr.FeedDocument()
#    fr.CutType = 2
    fr.StringQuantity = 15
    fr.FeedDocument()
    if cut_invoice:
        fr.CutCheck()
    print(fr.ResultCode, fr.ResultCodeDescription)
    fr.Disconnect()
    # return order
    return {"message": "Invoice printed successfully"}

@app.post("/api/v1/payment/cash")
async def process_cash_payment(order: Order):
    result = await order_pay(order, "cash")
    return result

@app.post("/api/v1/payment/card")
async def process_card_payment(order: Order):
    result = await order_pay(order, "card")
    return result

@app.post("/api/v1/print/invoice")
async def print_invoice(order: Order):
    # Logic for printing invoice
    return {"message": "Invoice printed successfully"}

@app.post("/api/v1/print/kitchen-mark")
async def print_kitchen_mark(order: KitchenMarkRequest):
    try:
        # Подключение к принтеру
        p = Network(order.printer_ip)

        # Отключение китайского режима
        p._raw(b'\x1C\x2E')

        # Установка кодовой таблицы CP866 (русский язык)
        p._raw(b'\x1B\x74\x10')

        # Заголовок — номер заказа
        p.set(align='center', width=2, height=1)
        p.text(f"ЗАКАЗ №{order.order_number}\n")

        # Печать типа кухни (например, "КУХНЯ" или "БАР")
        p.set(align='center', width=2, height=2)
        p.text(f"== {order.kitchen_type.upper()} ==\n")

        p.set(align='left', width=1, height=1)
        p.text("=" * 48 + "\n")
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        p.text(f"СТОЛ: {order.table_number:<5}   ОФИЦИАНТ: {order.waiter_name:<20}\n")
        p.text(f"ВРЕМЯ: {now}\n")
        p.text("=" * 48 + "\n")

        # Позиции с точками
        for item in order.products:
            name = item.name[:35]  # обрезаем длинные названия
            qty_str = f"{item.quantity} шт"
            dots = "." * (48 - len(name) - len(qty_str))
            p.text(f"{name}{dots}{qty_str}\n")

        p.text("=" * 48 + "\n")

        # Подача бумаги и частичная обрезка
        p._raw(b'\x1B\x64\x02')
        p.cut(mode='PART')
        p._raw(b'\x1B\x64\x02')

        return {"message": "Kitchen mark printed successfully"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/print/xreport")
async def print_x_report():
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    fr.Password = 30
    fr.PrintReportWithoutCleaning()
    print(fr.ResultCode, fr.ResultCodeDescription)
    fr.WaitForPrinting()
    fr.Disconnect()
    return {"message": "X-report printed successfully"}

@app.post("/api/v1/print/zreport")
async def print_z_report(employee: Employee):
    print(employee)
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    fr.Password = 30
    fr.FNBeginCloseSession()
    send_tag_1021_1203(fr, employee.pos + " " + employee.fio, employee.inn)
    fr.FNCloseSession()
    print(fr.ResultCode, fr.ResultCodeDescription)
    fr.WaitForPrinting()
    # return fr.ECRMode, fr.ECRModeDescription
    fr.Disconnect()
    return {"message": "Z-report printed successfully"}

def kill_document():
    """
    Функция прибития застрявшего документа (SysAdminCancelCheck)
    """
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    fr.Password = 30
    fr.SysAdminCancelCheck()
    print('Аннулировали документ')
    result = {'ResultCode': fr.ResultCode, 'ResultCodeDescription': fr.ResultCodeDescription}
    fr.Disconnect()
    return result

@app.post("/api/v1/cancel-document")
async def cancel_document():
    result = kill_document()
    return {"message": "Document cancelled", **result}

def validate_egais_fields(inn, kpp, kassa, address, name, number, shift):
    """
    Валидация полей согласно XSD схеме ПРИЛОЖЕНИЕ Б
    """
    import re
    
    # Валидация ИНН (10 или 12 цифр)
    if not re.match(r'^\d{10}$|^\d{12}$', str(inn)):
        raise ValueError(f"ИНН должен содержать 10 или 12 цифр: {inn}")
    
    # Валидация КПП (9 цифр или пустая строка)
    if kpp and not re.match(r'^\d{9}$', str(kpp)):
        raise ValueError(f"КПП должен содержать 9 цифр: {kpp}")
    
    # Валидация адреса (максимум 128 символов)
    if len(str(address)) > 128:
        raise ValueError(f"Адрес не должен превышать 128 символов: {len(str(address))}")
    
    # Валидация названия (максимум 128 символов)
    if len(str(name)) > 128:
        raise ValueError(f"Название не должно превышать 128 символов: {len(str(name))}")
    
    return True

def validate_bottle_fields(price, barcode, ean=None, volume=None):
    """
    Валидация полей элемента Bottle согласно XSD схеме
    """
    import re
    
    # Валидация цены (формат: [-]?\d+\.\d{0,2})
    if not re.match(r'^[-]?\d+\.\d{0,2}$', str(price)):
        raise ValueError(f"Цена должна быть в формате [-]?\\d+\\.\\d{{0,2}}: {price}")
    
    # Валидация баркода (формат: \d\d[a-zA-Z0-9]{21}\d[0-1]\d[0-3]\d{10}[a-zA-Z0-9]{31})
    if not re.match(r'^\d\d[a-zA-Z0-9]{21}\d[0-1]\d[0-3]\d{10}[a-zA-Z0-9]{31}$', str(barcode)):
        raise ValueError(f"Баркод не соответствует формату: {barcode}")
    
    # Валидация EAN (8, 12, 13 или 14 цифр)
    if ean and not re.match(r'^\d{8}$|^\d{12}$|^\d{13}$|^\d{14}$', str(ean)):
        raise ValueError(f"EAN должен содержать 8, 12, 13 или 14 цифр: {ean}")
    
    # Валидация объема (формат: \d+\.?\d{0,4})
    if volume and not re.match(r'^\d+\.?\d{0,4}$', str(volume)):
        raise ValueError(f"Объем должен быть в формате \\d+\\.?\\d{0,4}: {volume}")
    
    return True

def build_egais_cheque_xml(order, alco_items, last_check_info=None):
    """
    Построение XML чека согласно схеме WB_DOC_SINGLE_01 для отправки в УТМ ЕГАИС
    Использует простую структуру как в примере egais_cheque_example.xml
    """
    # Получаем данные организации из переменных окружения или кэша ККТ
    kassa = last_check_info.get('KKTNumber') if last_check_info else os.getenv("KASSA", "45664")
    number = last_check_info.get('FDNumber') if last_check_info and last_check_info.get('FDNumber') else "1"
    
    # Используем актуальный номер смены из check_info или значение по умолчанию
    shift = last_check_info.get('ShiftNumber') if last_check_info and last_check_info.get('ShiftNumber') else "1"
    
    # Используем актуальное время из check_info или текущее время
    if last_check_info and last_check_info.get('EgaisDateTime'):
        datetime_str = last_check_info.get('EgaisDateTime')
        # Преобразуем DDMMYYHHMM в ISO формат для ChequeV3
        day = datetime_str[:2]
        month = datetime_str[2:4]
        year = "20" + datetime_str[4:6]
        hour = datetime_str[6:8]
        minute = datetime_str[8:10]
        iso_datetime = f"{year}-{month}-{day}T{hour}:{minute}:00"
    else:
        now = datetime.now()
        iso_datetime = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Определяем тип чека
    cheque_type = "Продажа" if order.typedoc != "return" else "Возврат"
    
    # Получаем FSRAR_ID из переменных окружения
    fsrar_id = os.getenv("FSRAR_ID", "020000347275")
    
    # Логируем используемые параметры
    print(f"EGАИС ChequeV3 XML параметры: смена={shift}, время={iso_datetime}, касса={kassa}, тип={cheque_type}")
    
    # Создаем корневой элемент Documents с правильными namespace
    documents = ET.Element("ns:Documents")
    documents.set("Version", "1.0")
    documents.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    documents.set("xmlns:ns", "http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01")
    documents.set("xmlns:ck", "http://fsrar.ru/WEGAIS/ChequeV3")
    documents.set("xmlns:oref", "http://fsrar.ru/WEGAIS/ClientRef_v2")
    documents.set("xmlns:pref", "http://fsrar.ru/WEGAIS/ProductRef_v2")
    
    # Добавляем Owner
    owner = ET.SubElement(documents, "ns:Owner")
    fsrar_id_elem = ET.SubElement(owner, "ns:FSRAR_ID")
    fsrar_id_elem.text = fsrar_id
    
    # Добавляем Document
    document = ET.SubElement(documents, "ns:Document")
    
    # Добавляем ChequeV3
    cheque = ET.SubElement(document, "ns:ChequeV3")
    
    # Добавляем Header (только для продаж, как в примере)
    header = ET.SubElement(cheque, "ck:Header")
    
    # Дата и время
    date_elem = ET.SubElement(header, "ck:Date")
    date_elem.text = iso_datetime
    
    # Касса
    kassa_elem = ET.SubElement(header, "ck:Kassa")
    kassa_elem.text = str(kassa)
    
    # Смена
    shift_elem = ET.SubElement(header, "ck:Shift")
    shift_elem.text = str(shift)
    
    # Номер чека
    number_elem = ET.SubElement(header, "ck:Number")
    number_elem.text = str(number)
    
    # Тип чека
    type_elem = ET.SubElement(header, "ck:Type")
    type_elem.text = cheque_type
    
    # Content
    content = ET.SubElement(cheque, "ck:Content")
    
    # Добавляем элементы Bottle для каждой алкогольной позиции (только как в примере)
    for item in alco_items:
        bottle = ET.SubElement(content, "ck:Bottle")
        
        # Баркод (обязательный элемент)
        barcode = item.egais_mark_code or item.alc_code
        
        barcode_elem = ET.SubElement(bottle, "ck:Barcode")
        barcode_elem.text = barcode
        
        # EAN код (обязательный элемент)
        ean = str(item.GTIN)
        ean_elem = ET.SubElement(bottle, "ck:EAN")
        ean_elem.text = ean
        
        # Цена (обязательный элемент)
        price = f"{float(item.price):.2f}"
        price_elem = ET.SubElement(bottle, "ck:Price")
        price_elem.text = price
    
    xml_bytes = ET.tostring(documents, encoding='utf-8', xml_declaration=True)
    return xml_bytes

def build_egais_v4_xml(order, alco_items, last_check_info=None):
    """
    Построение XML чека согласно схеме ChequeV3 для отправки в УТМ ЕГАИС
    Использует новую схему ChequeV3 вместо старой Ticket/Document/Receipt структуры
    """
    return build_egais_cheque_xml(order, alco_items, last_check_info)

def print_egais_qr(qr_string):
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    fr.Barcode = qr_string
    fr.PrintBarcode()
    fr.Disconnect()

async def send_egais_check(order: Order, check_info=None):
    """
    Отправка чека с алкогольной позицией в ЕГАИС (v4 XML через УТМ) и печать QR-кода при успехе
    Если EGAIS_SEND != true, только сохраняет исходный XML в файл.
    """
    egais_host = os.getenv('EGAIS_HOST', 'http://localhost:8080')
    egais_send = os.getenv('EGAIS_SEND', 'false').lower() == 'true'
    alco_items = [item for item in order.products if item.mark == '1' or item.alc_code or item.egais_mark_code]
    if not alco_items:
        await save_egais_result(
            status="error",
            order_data=order.dict(),
            error="В заказе нет алкогольных позиций для ЕГАИС"
        )
        return {"message": "В заказе нет алкогольных позиций для ЕГАИС"}
    try:
        xml_data = build_egais_v4_xml(order, alco_items, last_check_info=check_info)
        ts = time.strftime('%Y%m%d_%H%M%S')
        
        # Создаем папку check если её нет
        check_dir = "check"
        if not os.path.exists(check_dir):
            os.makedirs(check_dir)
        
        xml_filename = f"egais_xml_{ts}.xml"
        xml_filepath = os.path.join(check_dir, xml_filename)
        with open(xml_filepath, "wb") as f:
            f.write(xml_data)
        if not egais_send:
            await save_egais_result(
                status="saved",
                order_data=order.dict(),
                xml_data=xml_data.decode('utf-8'),
                xml_file=xml_filename
            )
            return {"message": "EGAIS_SEND is not true, XML сохранён в файл", "xml_file": xml_filepath}
        files = {'xml_file': ('Cheque.xml', xml_data, 'application/xml')}
        response = requests.post(f"{egais_host}/xml", files=files, timeout=10)
        response.raise_for_status()
        # Сохраняем ответ в файл
        filename = f"egais_response_{ts}.txt"
        filepath = os.path.join(check_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=== ОТВЕТ ЕГАИС ===\n")
            f.write(response.text)
        # Попытка найти QR-код в ответе (ищем тег <QRCode> или поле qr_code)
        qr_code = None
        try:
            import re
            match = re.search(r'<QRCode>(.*?)</QRCode>', response.text)
            if match:
                qr_code = match.group(1)
            else:
                import json
                data = response.json()
                qr_code = data.get('qr_code')
        except Exception:
            pass
        if qr_code:
            print_egais_qr(qr_code)
        # Сохраняем успешный результат в БД
        await save_egais_result(
            status="success",
            order_data=order.dict(),
            xml_data=xml_data.decode('utf-8'),
            response_data=response.text,
            qr_code=qr_code,
            xml_file=xml_filepath,
            saved_file=filepath
        )
        return {"message": "Чек v4 отправлен в ЕГАИС", "egais_response": response.text, "qr_code": qr_code, "saved_file": filepath, "xml_file": xml_filepath}
    except Exception as e:
        # Сохраняем ошибку в БД
        await save_egais_result(
            status="error",
            order_data=order.dict(),
            xml_data=xml_data.decode('utf-8') if 'xml_data' in locals() else None,
            error=str(e)
        )
        return {"error": str(e)}

@app.post("/api/v1/send-egais-check")
async def api_send_egais_check(order: Order):
    """
    API endpoint для отправки чека с алкогольной позицией в ЕГАИС
    """
    return await send_egais_check(order)

@app.post("/api/v1/send-egais-xml")
async def api_send_egais_xml(xml_file: UploadFile = File(...), description: str = Form("")):
    """
    API endpoint для отправки XML файла в ЕГАИС
    """
    try:
        # Читаем содержимое XML файла
        xml_content = await xml_file.read()
        
        # Проверяем, что это XML файл
        if not xml_file.filename.endswith('.xml'):
            return {"error": "Файл должен иметь расширение .xml"}
        
        # Создаем папку check если её нет
        check_dir = "check"
        if not os.path.exists(check_dir):
            os.makedirs(check_dir)
        
        # Сохраняем оригинальный файл
        ts = time.strftime('%Y%m%d_%H%M%S')
        original_filename = f"egais_xml_upload_{ts}.xml"
        original_filepath = os.path.join(check_dir, original_filename)
        
        with open(original_filepath, "wb") as f:
            f.write(xml_content)
        
        # Получаем настройки EGAIS
        egais_host = os.getenv('EGAIS_HOST', 'http://localhost:8080')
        egais_send = os.getenv('EGAIS_SEND', 'false').lower() == 'true'
        
        if not egais_send:
            await save_egais_result(
                status="saved",
                order_data={"description": description, "filename": xml_file.filename},
                xml_data=xml_content.decode('utf-8'),
                xml_file=original_filepath
            )
            return {
                "message": "EGAIS_SEND is not true, XML сохранён в файл", 
                "xml_file": original_filepath
            }
        
        # Отправляем в EGAIS
        files = {'xml_file': ('Cheque.xml', xml_content, 'application/xml')}
        response = requests.post(f"{egais_host}/xml", files=files, timeout=10)
        response.raise_for_status()
        
        # Сохраняем ответ в файл
        response_filename = f"egais_response_{ts}.txt"
        response_filepath = os.path.join(check_dir, response_filename)
        with open(response_filepath, "w", encoding="utf-8") as f:
            f.write("=== ОТВЕТ ЕГАИС ===\n")
            f.write(response.text)
        
        # Попытка найти QR-код в ответе
        qr_code = None
        try:
            import re
            match = re.search(r'<QRCode>(.*?)</QRCode>', response.text)
            if match:
                qr_code = match.group(1)
            else:
                import json
                data = response.json()
                qr_code = data.get('qr_code')
        except Exception:
            pass
        
        # Печатаем QR-код если есть
        if qr_code:
            print_egais_qr(qr_code)
        
        # Сохраняем успешный результат в БД
        await save_egais_result(
            status="success",
            order_data={"description": description, "filename": xml_file.filename},
            xml_data=xml_content.decode('utf-8'),
            response_data=response.text,
            qr_code=qr_code,
            xml_file=original_filepath,
            saved_file=response_filepath
        )
        
        return {
            "message": "XML документ отправлен в ЕГАИС", 
            "egais_response": response.text, 
            "qr_code": qr_code, 
            "saved_file": response_filepath, 
            "xml_file": original_filepath
        }
        
    except Exception as e:
        # Сохраняем ошибку в БД
        await save_egais_result(
            status="error",
            order_data={"description": description, "filename": xml_file.filename},
            xml_data=xml_content.decode('utf-8') if 'xml_content' in locals() else None,
            error=str(e)
        )
        return {"error": str(e)}

def initialize_kkt_cache():
    """
    Инициализировать кэш данных ККТ при старте приложения
    """
    global KKT_CACHE
    try:
        fr = win32com.client.Dispatch('Addin.DRvFR')
        fr.Connect()
        fr.Password = 30
        
        # Получаем данные фискализации ФН
        fr.GetECRStatus()
        KKT_CACHE['INN'] = getattr(fr, 'INN', None)
        fr.ReadSerialNumber()
        KKT_CACHE['KKTSerialNumber'] = getattr(fr, 'SerialNumber', None)
        
        # Получаем серийный номер ККТ и регистрационный номер
        fr.FNGetFiscalizationResult()
        KKT_CACHE['KKTRegistrationNumber'] = getattr(fr, 'KKTRegistrationNumber', None)
        
        # Получаем серийный номер ФН
        fr.FNGetSerial()
        KKT_CACHE['FNSerialNumber'] = getattr(fr, 'SerialNumber', None)
        
        fr.Disconnect()
        KKT_CACHE['initialized'] = True
        
        print(f"Кэш ККТ инициализирован: INN={KKT_CACHE['INN']}, KKTRegNumber={KKT_CACHE['KKTRegistrationNumber']}, KKTSerialNumber={KKT_CACHE['KKTSerialNumber']}, FNSerialNumber={KKT_CACHE['FNSerialNumber']}")
        
    except Exception as e:
        print(f"Ошибка инициализации кэша ККТ: {e}")
        KKT_CACHE['initialized'] = False

def get_ecr_status(fr):
    """
    Получить статус ККТ (ECRStatus)
    """
    try:
        fr.Password = 30
        fr.GetECRStatus()
        return {
            'ECRMode': getattr(fr, 'ECRMode', None),
            'ECRModeDescription': getattr(fr, 'ECRModeDescription', None),
            'DocumentNumber': getattr(fr, 'DocumentNumber', None),
            'ResultCode': fr.ResultCode,
            'ResultCodeDescription': fr.ResultCodeDescription
        }
    except Exception as e:
        return {'error': str(e)}

def get_fn_expiration_time():
    """
    Получить срок действия ФН (FNGetExpirationTime)
    """
    try:
        fr = win32com.client.Dispatch('Addin.DRvFR')
        fr.Connect()
        fr.Password = 30
        
        # Запрос срока действия ФН
        fr.FNGetExpirationTime()
        
        fn_expiration = {
            'Date': getattr(fr, 'Date', None),
            'ResultCode': fr.ResultCode,
            'ResultCodeDescription': fr.ResultCodeDescription
        }
        
        fr.Disconnect()
        
        return {
            "status": "success",
            "fn_expiration": fn_expiration
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_fn_current_session_params():
    """
    Получить параметры текущей смены ФН (FNGetCurrentSessionParams)
    Возвращает состояние смены, номер смены и номер чека
    """
    try:
        fr = win32com.client.Dispatch('Addin.DRvFR')
        fr.Connect()
        fr.Password = 30
        
        # Вызываем FNGetCurrentSessionParams
        fr.FNGetCurrentSessionParams()
        
        # Получаем параметры смены
        session_params = {
            "fn_session_state": getattr(fr, 'FNSessionState', None),  # Состояние смены (0-255)
            "session_number": getattr(fr, 'SessionNumber', None),      # Номер смены (0-FFFFh)
            "receipt_number": getattr(fr, 'ReceiptNumber', None),      # Номер чека (0-FFFFh)
            "result_code": fr.ResultCode,
            "result_description": fr.ResultCodeDescription
        }
        
        fr.Disconnect()
        
        return {
            "status": "success",
            "session_params": session_params
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_kkt_info():
    """
    Получить общие параметры ККТ включая DocumentNumber
    """
    try:
        fr = win32com.client.Dispatch('Addin.DRvFR')
        fr.Connect()
        fr.Password = 30
        
        kkt_info = {}
        
        # Получаем статус ККТ
        kkt_info['ECRStatus'] = get_ecr_status(fr)
        
        # Получаем статус ФН
        try:
            fr.FNGetStatus()
            kkt_info['FNStatus'] = {
                'FNLifeState': getattr(fr, 'FNLifeState', None),
                'FNCurrentDocument': getattr(fr, 'FNCurrentDocument', None),
                'FNDocumentData': getattr(fr, 'FNDocumentData', None),
                'FNSessionState': getattr(fr, 'FNSessionState', None),
                'FNWarningFlags': getattr(fr, 'FNWarningFlags', None),
                'Date': getattr(fr, 'Date', None),
                'Time': getattr(fr, 'Time', None),
                'SerialNumber': getattr(fr, 'SerialNumber', None),
                'DocumentNumber': getattr(fr, 'DocumentNumber', None),
                'ResultCode': fr.ResultCode,
                'ResultCodeDescription': fr.ResultCodeDescription
            }
        except Exception as e:
            kkt_info['FNStatus'] = {'error': str(e)}
        
        # Получаем итоги фискализации ФН
        try:
            fr.FNGetFiscalizationResult()
            kkt_info['FNFiscalization'] = {
                'Date': getattr(fr, 'Date', None),
                'INN': getattr(fr, 'INN', None),
                'KKTRegistrationNumber': getattr(fr, 'KKTRegistrationNumber', None),
                'TaxType': getattr(fr, 'TaxType', None),
                'WorkMode': getattr(fr, 'WorkMode', None),
                'RegistrationReasonCode': getattr(fr, 'RegistrationReasonCode', None),
                'DocumentNumber': getattr(fr, 'DocumentNumber', None),
                'FiscalSign': getattr(fr, 'FiscalSign', None),
                'ResultCode': fr.ResultCode,
                'ResultCodeDescription': fr.ResultCodeDescription
            }
        except Exception as e:
            kkt_info['FNFiscalization'] = {'error': str(e)}
        
        # Получаем срок действия ФН
        try:
            fr.FNGetExpirationTime()
            kkt_info['FNExpiration'] = {
                'Date': getattr(fr, 'Date', None),
                'ResultCode': fr.ResultCode,
                'ResultCodeDescription': fr.ResultCodeDescription
            }
        except Exception as e:
            kkt_info['FNExpiration'] = {'error': str(e)}
        
        fr.Disconnect()
        
        return {
            "status": "success",
            "kkt_info": kkt_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/v1/kkt-info")
async def api_get_kkt_info():
    """
    API endpoint для получения общих параметров ККТ включая DocumentNumber
    """
    return get_kkt_info()

@app.get("/api/v1/fn-expiration")
async def api_get_fn_expiration():
    """
    API endpoint для получения срока действия ФН
    """
    return get_fn_expiration_time()

@app.get("/api/v1/fn-session-params")
async def api_get_fn_session_params():
    """
    API endpoint для получения параметров текущей смены ФН
    """
    return get_fn_current_session_params()

@app.get("/api/v1/logs/checks")
async def get_check_logs(page: int = 1, limit: int = 50, status: str = None):
    """
    Получить список логов чеков с пагинацией
    """
    global db_connected
    if not db_connected:
        return {"status": "error", "message": "База данных не подключена"}
    
    try:
        offset = (page - 1) * limit
        query = CheckLog.all().order_by('-timestamp')
        
        if status:
            query = query.filter(status=status)
        
        total = await query.count()
        logs = await query.offset(offset).limit(limit)
        
        return {
            "status": "success",
            "data": [log.__dict__ for log in logs],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/v1/logs/egais")
async def get_egais_logs(page: int = 1, limit: int = 50, status: str = None):
    """
    Получить список логов ЕГАИС с пагинацией
    """
    global db_connected
    if not db_connected:
        return {"status": "error", "message": "База данных не подключена"}
    
    try:
        offset = (page - 1) * limit
        query = EgaisLog.all().order_by('-timestamp')
        
        if status:
            query = query.filter(status=status)
        
        total = await query.count()
        logs = await query.offset(offset).limit(limit)
        
        return {
            "status": "success",
            "data": [log.__dict__ for log in logs],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/v1/logs/stats")
async def get_logs_stats():
    """
    Получить статистику по логам
    """
    global db_connected
    if not db_connected:
        return {"status": "error", "message": "База данных не подключена"}
    
    try:
        # Статистика по чекам
        check_stats = {
            "total": await CheckLog.all().count(),
            "success": await CheckLog.filter(status="success").count(),
            "error": await CheckLog.filter(status="error").count()
        }
        
        # Статистика по ЕГАИС
        egais_stats = {
            "total": await EgaisLog.all().count(),
            "success": await EgaisLog.filter(status="success").count(),
            "error": await EgaisLog.filter(status="error").count(),
            "saved": await EgaisLog.filter(status="saved").count()
        }
        
        return {
            "status": "success",
            "checks": check_stats,
            "egais": egais_stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
