#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2017/2/24.

from datetime import datetime
from argeweb import auth, add_authorizations, require_post
from argeweb import Controller, scaffold, route_with, route
from argeweb.components.pagination import Pagination
from argeweb.components.csrf import CSRF, csrf_protect
from argeweb.components.search import Search
from ..models.user_contact_data_model import UserContactDataModel


class Form(Controller):
    class Meta:
        default_view = 'json'
        Model = UserContactDataModel

    class Scaffold:
        display_in_form = ['name', 'account', 'is_enable', 'sort', 'created', 'modified']
        display_in_list = ['name', 'account']

    @route
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
            if application_user is None:
                self.context['message'] = u'舊密碼有誤，請重新輸入'
                return
            else:
                if application_user.need_check_old_password:
                    if application_user.check_password(input_old_password) is False:
                        self.context['message'] = u'舊密碼有誤，請重新輸入'
                        return
            need_change_password = True
        if application_user is None:
            self.context['message'] = u'使用者帳號不存在?'
            return
        contact_data = self.meta.Model.get_or_create(application_user)
        if need_change_password:
            application_user.need_check_old_password = True
            contact_data.password = input_password

        if self.params.has('email'):
            if contact_data.email != self.params.get_string('email'):
                contact_data.email = self.params.get_string('email')
                contact_data.is_email_verified = False
            if contact_data.last_verified_email == self.params.get_string('email'):
                contact_data.is_email_verified = True
        if self.params.has('birthday'):
            try:
                day = self.params.get_datetime('birthday')
            except:
                day = datetime.now()
        else:
            day = datetime.now()

        contact_data.birthday_year = day.year
        contact_data.birthday_month = day.month
        contact_data.birthday_day = day.day

        for filed_name, f in self.meta.Model._properties.items():
            field_value = self.params.get_string(filed_name, None)
            if field_value:
                setattr(contact_data, filed_name, field_value)

        if self.params.has('user_name'):
            contact_data.user_name_proxy = self.params.get_string('user_name')

        contact_data.update_user(application_user)
        contact_data.put()
        self.context['data'] = {'result': 'success'}
        self.context['message'] = u'修改完成'

    @route
    @route_with(name='form:user:send_mobile_code')
    def send_mobile_code(self):
        application_user = self.application_user
        if application_user is None:
            return self.json_failure_message(u'使用者帳號不存在')
        mobile = self.params.get_mobile_number('mobile')
        if mobile is None:
            return self.json_failure_message(u'請輸入手機')

        self.fire('before_user_request_verified_mobile', user=application_user, mobile=mobile)
        contact_data = self.meta.Model.get_or_create(application_user)
        contact_data.gen_mobile_verification_code(mobile)
        contact_data.put()
        r = self.fire('user_request_verified_mobile',
                      send_to=mobile,
                      user=application_user, code=contact_data.mobile_verification_code)
        self.fire('after_user_request_verified_mobile', user=application_user, mobile=mobile)
        for item in r:
            if item['status'] == 'success':
                return self.json_success_message(u'驗証簡訊已寄出給 %s' % mobile)
            else:
                return self.json_failure_message(u'驗証簡訊寄送失敗 %s' % item['message'])
        return self.json_failure_message(u'驗証簡訊寄送失敗')

    @route
    @route_with(name='form:user:check_mobile_code')
    def check_mobile_code(self):
        application_user = self.application_user
        if application_user is None:
            return self.json_failure_message(u'使用者帳號不存在')
        user_data = self.meta.Model.get_or_create(self.application_user)
        mobile_code = self.params.get_string('mobile_code')
        if mobile_code is None or mobile_code is u'':
            return self.json_failure_message(u'請輸入驗証碼')
        self.fire('before_user_verified_mobile', user=application_user, code=mobile_code)
        r = user_data.verify_mobile(mobile_code)
        if r is False:
            self.context['data'] = {
                'data': user_data,
                'r': r,
                'code': mobile_code
            }
            return self.json_failure_message(u'驗証失敗')
        self.context['data'] = {'result': 'success', 'mobile': user_data.last_verified_mobile}
        self.context['message'] = u'驗証成功'
        self.fire('after_user_verified_mobile', user=application_user)
        if user_data.is_email_verified_proxy is True:
            self.fire('after_user_verified_both', user=application_user)

    @route
    @route_with(name='form:user:send_email_code')
    def send_email_code(self):
        self.context['data'] = {'result': 'failure'}
        application_user = self.application_user
        if application_user is None:
            self.context['message'] = u'使用者帳號不存在?'
            return
        email = self.params.get_email('email')
        if email is None:
            self.context['message'] = u'請輸入信箱'
            return
        contact_data = self.meta.Model.get_or_create(application_user)
        contact_data.gen_email_verification_code(email)
        contact_data.put()

        r = self.fire('user_request_verified_email',
                      send_to=email,
                      user=application_user, code=contact_data.email_verification_code)
        for item in r:
            if item['status'] == 'success':
                self.context['data'] = {'result': 'success'}
                self.context['message'] = u'驗証郵件已寄出給 %s' % email
            else:
                self.context['data'] = {'result': item['status']}
                self.context['message'] = item['message']

    @route
    @route_with(name='form:user:check_email_code')
    def check_email_code(self):
        self.context['data'] = {'result': 'failure'}
        application_user = self.params.get_ndb_record(u'user')
        if application_user is None:
            application_user = self.application_user
        else:
            self.session['application_user_key'] = application_user.key

        if application_user is None:
            self.context['message'] = u'使用者帳號不存在?'
            return
        user_data = self.meta.Model.get_or_create(application_user)
        email_code = self.params.get_string('email_code')
        if email_code is None or email_code is u'':
            self.context['message'] = u'請輸入驗証碼'
            return
        r = user_data.verify_email(email_code)
        if r is False:
            self.context['message'] = u'驗証失敗'
            return
        self.context['data'] = {'result': 'success', 'email': user_data.last_verified_email}
        self.context['message'] = u'驗証成功'
        self.fire('after_user_verified_email', user=application_user)
        if user_data.is_mobile_verified is True:
            self.fire('after_user_verified_both', user=application_user)

    @route
    @require_post
    @route_with(name='form:user:login_by_email_or_mobile')
    def login_by_email_or_mobile(self):
        input_remember_account = self.params.get_string('remember_account')
        input_email = self.params.get_string('email_or_mobile')
        input_mobile = self.params.get_string('email_or_mobile')
        input_password = self.params.get_string('password').strip()
        if input_email == u'' or input_password == u'':
            return self.json_failure_message(u'帳號密碼不可為空')

        from plugins.application_user.models.application_user_model import ApplicationUserModel
        application_user_data_list = self.meta.Model.find_by_properties(mobile=input_mobile).fetch()
        for application_user_data in application_user_data_list:
            if application_user_data is not None:
                user = application_user_data.user.get()
                if user:
                    input_email = user.email
        application_user = ApplicationUserModel.get_user_by_email_and_password(input_email, input_password)
        if application_user is not None:
            if input_remember_account:
                self.session['remember_account'] = self.params.get_string('email_or_mobile')
            self.session['application_user_key'] = application_user.key
            return self.json_success_message(u'登入成功')
        return self.json_failure_message(u'帳號密碼有誤，或帳號不存在')

    @route
    @require_post
    @route_with(name='form:user:login_by_mobile')
    def login_by_mobile(self):
        input_remember_account = self.params.get_string('remember_account')
        input_mobile = self.params.get_string('mobile')
        input_password = self.params.get_string('password').strip()
        if input_mobile == u'' or input_password == u'':
            return self.json_failure_message(u'帳號密碼不可為空')

        application_user = None
        application_user_data_list = self.meta.Model.find_by_properties(mobile=input_mobile).fetch()
        for application_user_data in application_user_data_list:
            user = application_user_data.user.get()
            if user and user.check_password(input_password):
                application_user = user
        if application_user is not None:
            if input_remember_account:
                self.session['remember_account'] = self.params.get_string('email_or_mobile')
            self.session['application_user_key'] = application_user.key
            return self.json_success_message(u'登入成功')
        return self.json_failure_message(u'帳號密碼有誤，或帳號不存在')