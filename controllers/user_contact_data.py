#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.

from argeweb import Controller, scaffold, route_menu, route_with, route, settings
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search


class UserContactData(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)

    class Scaffold:
        display_in_form = ('account', 'created', 'modified')
        hidden_in_form = ('name', 'is_enable')
        display_in_list = ('user_name_proxy', 'user_email_proxy', 'telephone', 'mobile', 'address_city', 'address_district')

    @route_menu(list_name=u'backend', text=u'聯絡資料', sort=9803, icon='users', group=u'帳號管理', need_hr_parent=True)
    def admin_list(self):
        scaffold.list(self)
