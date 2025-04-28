from typing import Union, List

from fastapi import FastAPI
from pydantic import BaseModel

from escpos.printer import Network

from datetime import datetime
import win32com.client
import argparse
import json

from dotenv import load_dotenv
import os

load_dotenv()

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

def add_spaces_to_45_chars(input_string):
    total_spaces = 45 - len(input_string)
    left_spaces = total_spaces // 2
    right_spaces = total_spaces - left_spaces
    # Добавляем пробелы слева и справа
    padded_string = " " * left_spaces + input_string + " " * right_spaces
    return padded_string

def get_ecr_status(fr: win32com.client.CDispatch):
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

def order_pay(order, type_pay) -> None:
    print(order)
    max_discount = os.getenv('MAX_DISCOUNT', 'False') in ['True']
    discount = 0
    total_to_pay = 0
    item_no_discount = False
    if float(order.alldiscount) > 0 and float(order.alldiscount) <= 100:
        discount = float(order.alldiscount) / 100    
    fr = win32com.client.Dispatch('Addin.DRvFR')
    fr.Connect()
    
    ecr_mode, ecr_description = get_ecr_status(fr)
    print(f"ECR Mode: {ecr_mode}, Description: {ecr_description}")
    
    fr.Summ1Enabled = False
    fr.TaxValueEnabled = False
    # fr.CheckType = 0;
    # fr.OpenCheck();
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
            # Заменяем {GS} на управляющий символ 29
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
    # print(fr.CheckSubTotal())
    if type_pay == "cash":
        fr.Summ1 = total_to_pay
    if type_pay == "card":
        fr.Summ2 = total_to_pay
    send_tag_1021_1203(fr, order.employee_pos + " " + order.employee_fio, order.employee_inn)
    fr.FNCloseCheckEx()
    print(fr.ResultCode, fr.ResultCodeDescription)
    #print(fr.CheckItemLocalResult)
    #print(fr.CheckItemLocalError)
    fr.StringQuantity = 2
    fr.FeedDocument()
    fr.CutType = 2
    fr.CutCheck()
    fr.Disconnect()

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
    if cut_invoice:
        fr.CutCheck()
    print(fr.ResultCode, fr.ResultCodeDescription)
    fr.Disconnect()
    # return order
    return {"message": "Invoice printed successfully"}

@app.post("/api/v1/payment/cash")
async def process_cash_payment(order: Order):
    order_pay(order, "cash")
    return {"message": "Cash payment processed successfully"}

@app.post("/api/v1/payment/card")
async def process_card_payment(order: Order):
    order_pay(order, "card")
    return {"message": "Card payment processed successfully"}

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
