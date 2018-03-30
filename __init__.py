#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.
from datetime import datetime
from argeweb import ViewDatastore
from argeweb.core.events import on
from .models.user_contact_data_model import UserContactDataModel


@on('after_user_delete')
def after_user_delete(controller, key, *args, **kwargs):
    data_list = UserContactDataModel.query(UserContactDataModel.user==key).fetch()
    for data in data_list:
        data.delete()


@on('before_order_checkout')
def before_order_checkout(controller, user, *args, **kwargs):
    data = UserContactDataModel.get_or_create(user=user)
    user.mobile = data.mobile


@on('after_user_signup')
def after_user_signup(controller, user, *args, **kwargs):
    contact_data = UserContactDataModel.get_or_create(user=user)

    for filed_name, f in UserContactDataModel._properties.items():
        field_value = controller.params.get_string(filed_name, None)
        if field_value:
            setattr(contact_data, filed_name, field_value)
    data = {}
    if 'data' in kwargs:
        data = kwargs['data']
    controller.logging.debug(data)
    birthday = None
    try:
        if 'birthday' in data:
            birthday = datetime.strptime(data['birthday'], '%d/%m/%Y')
        if controller.params.has('birthday') and birthday is None:
            birthday = controller.params.get_datetime('birthday')
    except:
        pass
    if birthday is None:
        birthday = datetime.now()

    contact_data.birthday_year = birthday.year
    contact_data.birthday_month = birthday.month
    contact_data.birthday_day = birthday.day

    if controller.params.has('user_name'):
        user.name = controller.params.get_string('user_name')
        user.put()
    contact_data.user_name_proxy = user.name
    contact_data.user_email_proxy = user.email
    contact_data.user_avatar_proxy = user.avatar
    contact_data.is_email_verified_proxy = user.is_email_verified

    if 'referrals' in controller.session:
        contact_data.referrals = controller.session['referrals']
    contact_data.put()
    return

ViewDatastore.register('user_data_list', UserContactDataModel.find_all_by_properties)
ViewDatastore.register('user_data', UserContactDataModel.get_or_create)

plugins_helper = {
    'title': u'使用者的聯絡資料',
    'desc': u'擴展網站使用者的資料欄位',
    'controllers': {
        'user_contact_data': {
            'group': u'聯絡資料',
            'actions': [
                {'action': 'list', 'name': u'聯絡資料管理'},
                {'action': 'add', 'name': u'新增聯絡資料'},
                {'action': 'edit', 'name': u'編輯聯絡資料'},
                {'action': 'view', 'name': u'檢視聯絡資料'},
                {'action': 'delete', 'name': u'刪除聯絡資料'},
                {'action': 'plugins_check', 'name': u'啟用停用模組'},
            ]
        }
    }
}
