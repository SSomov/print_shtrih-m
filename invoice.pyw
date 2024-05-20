import win32com.client
import argparse
import json

def kill_document(self):
    """
    функция прибития застрявшего документа
    :param comp_rec:  dict
    """
    fr.Password = 30
    fr.SysAdminCancelCheck()
    print('прибили документ')

fr = win32com.client.Dispatch('Addin.DRvFR')
fr.Connect()
kill_document(fr)   
fr.Disconnect()
print(fr.ResultCode, fr.ResultCodeDescription)
