#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.

from argeweb import ViewDatastore
from .models.user_contact_data_model import UserContactDataModel

ViewDatastore.register('user_data', UserContactDataModel.get_or_create)

plugins_helper = {
    'title': u'使用者的聯絡資料',
    'desc': u'擴展網站使用者的資料欄位',
    'controllers': {
        'user_contact_data': {
            'group': u'聯絡資料',
            'actions': [
                {'action': 'list', 'name': u'聯絡資料管理'},
                {'action': 'edit', 'name': u'編輯聯絡資料'},
                {'action': 'view', 'name': u'檢視聯絡資料'},
                {'action': 'delete', 'name': u'刪除聯絡資料'},
                {'action': 'plugins_check', 'name': u'啟用停用模組'},
            ]
        }
    }
}
