#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.
from argeweb import auth, add_authorizations
from argeweb import Controller, scaffold, route_menu, route_with, route, settings
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from plugins.mail import Mail
from ..models.user_contact_data_model import UserContactDataModel


class Form(Controller):
    class Meta:
        components = (scaffold.Scaffolding, Pagination, Search, CSRF)
        default_view = 'json'
        Model = UserContactDataModel

    class Scaffold:
        display_in_form = ('name', 'account', 'is_enable', 'sort', 'created', 'modified')
        display_in_list = ('name', 'account')

    @route
    @add_authorizations(auth.check_user)
    @route_with(name='form:user:change_contact_data')
    def change_contact_data(self):
        self.context['data'] = {'result': 'failure'}
        if self.request.method != 'POST':
            return self.abort(404)
        from plugins.application_user.models.application_user_model import ApplicationUserModel
        input_account_email = self.params.get_string('account_email')
        input_old_password = self.params.get_string('old_password')
        input_password = self.params.get_string('password')
        input_confirm_password = self.params.get_string('confirm_password')
        need_change_password = False
        application_user = self.application_user
        if input_old_password != u'' or input_password != u'':
            if input_password != input_confirm_password:
                self.context['message'] = u'密碼不相同，請輸入一致的密碼'
                return
            check_user_password = ApplicationUserModel.get_user_by_email_and_password(input_account_email, input_old_password)
            if application_user is None or check_user_password is None:
                self.context['message'] = u'舊密碼有誤，請重新輸入'
                return
            need_change_password = True
        if application_user is None:
            self.context['message'] = u'使用者帳號不存在?'
            return
        contact_data = self.meta.Model.get_or_create(application_user)
        if need_change_password:
            contact_data.password = input_password

        for key_name in ['telephone', 'mobile', 'address_country', 'address_city', 'address_district', 'address_detail', 'address_zip']:
            if self.params.has(key_name):
                setattr(contact_data, key_name, self.params.get_string(key_name))
        contact_data.put()
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'修改完成'
