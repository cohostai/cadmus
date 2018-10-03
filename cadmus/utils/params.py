#!/usr/bin/env python
# encoding: utf-8
"""
base

Copyright (c) 2018 __CGD Inc__. All rights reserved.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import boto3
from functools import partial


class ParametersStore(object):
    """
    The place where store parameters.
    """

    def get_params(self, *args, **kwargs):
        raise NotImplementedError

    def get_param(self, leaf_path):
        params = self.get_params()
        return params.get(leaf_path)


class AWSParametersStore(ParametersStore):

    def __init__(self,
                 region=os.getenv('REGION'),
                 application=os.getenv('APPLICATION'),
                 environment=os.getenv('ENVIRONMENT')):
        self._region = region
        self._application = application
        self._environment = environment

        self._ssm = boto3.client('ssm', region_name=self._region)
        self._ec2 = boto3.resource('ec2', region_name=self._region)

    def get_params(self, path=''):
        params = {}
        next_token = None
        path_prefix = '/{}/{}/{}'.format(self._application, self._environment, path)

        parameters_by_path = partial(
            self._ssm.get_parameters_by_path,
            Path=path_prefix,
            Recursive=True,
            WithDecryption=True
        )

        while True:
            if next_token:
                aws_parameters = parameters_by_path(NextToken=next_token)
            else:
                aws_parameters = parameters_by_path()

            next_token = aws_parameters.get('NextToken')
            params.update(
                self._extract_params(aws_parameters, path_prefix)
            )

            if not next_token:
                break

        return params

    @staticmethod
    def _extract_params(parameters, prefix):
        parameters = parameters['Parameters']
        param_by_name = {}

        for parameter in parameters:
            name = parameter['Name']
            name = name.replace(prefix, '')
            param_by_name.update({
                name: parameter['Value']
            })

        return param_by_name


class LocalParametersStore(ParametersStore):

    def get_params(self, *args):
        return os.environ


if os.getenv('PLATFORM', '').lower() == 'cloud':
    params_store = AWSParametersStore()
else:
    params_store = LocalParametersStore()
