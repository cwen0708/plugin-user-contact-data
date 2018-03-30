#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.

from argeweb import Controller, scaffold, route_menu
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.config_model import ConfigModel


class UserContactData(Controller):
    class Scaffold:
        hidden_in_form = ['name', 'user', 'is_enable']
        display_in_list = ['user_name_proxy', 'user_email_proxy', 'telephone', 'mobile', 'address_city', 'address_district']

    @route_menu(list_name=u'backend', group=u'帳號管理', text=u'聯絡資料', sort=9803, icon='users', need_hr=True)
    def admin_list(self):
        scaffold.list(self)

    def admin_edit(self, key):
        scaffold.edit(self, key)
        contact_data = self.context[self.scaffold.singular]
        contact_data.update_user()

    def before_scaffold(self):
        super(UserContactData, self).before_scaffold()
        config = ConfigModel.get_config()
        self.scaffold.change_field_visibility('referrals', config.use_referrals)
        self.scaffold.change_field_visibility('is_referrals_change', config.use_referrals)
        self.scaffold.change_field_visibility('birthday_year', config.use_birthday)
        self.scaffold.change_field_visibility('birthday_month', config.use_birthday)
        self.scaffold.change_field_visibility('birthday_day', config.use_birthday)
