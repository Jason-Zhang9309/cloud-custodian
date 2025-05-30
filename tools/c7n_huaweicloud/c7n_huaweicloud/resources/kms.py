# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging
import uuid

from huaweicloudsdkkms.v2 import (EnableKeyRotationRequest, OperateKeyRequestBody,
                                  DisableKeyRotationRequest, EnableKeyRequest,
                                  DisableKeyRequest, CreateKeyRequest, CreateKeyRequestBody,
                                  ListKeysRequest, ListKeysRequestBody)
from c7n.filters import ValueFilter
from c7n.utils import type_schema
from c7n_huaweicloud.actions.base import HuaweiCloudBaseAction
from c7n_huaweicloud.provider import resources
from c7n_huaweicloud.query import QueryResourceManager, TypeInfo

log = logging.getLogger("custodian.huaweicloud.resources.kms")


@resources.register('kms')
class Kms(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'kms'
        enum_spec = ("list_keys", 'key_details', 'offset')
        id = 'key_id'
        tag_resource_type = 'kms'
        config_resource_support = True


@Kms.action_registry.register("enable_key_rotation")
class rotationKey(HuaweiCloudBaseAction):
    """rotation kms key.

    :Example:

    .. code-block:: yaml

policies:
  - name: enable_key_rotation
    resource: huaweicloud.kms
    filters:
        - type: value
          key: key_rotation_enabled
          value: "False"
        - type: value
          key: domain_id
          value: "aaaaaaa"
    actions:
      - enable_key_rotation
    """

    schema = type_schema("enable_key_rotation")

    def perform_action(self, resource):

        notSupportList = {"RSA_2048", "RSA_3072", "RSA_4096", "EC_P256", "EC_P384",
                          "SM2", "ML_DSA_44", "ML_DSA_65", "ML_DSA_87"}
        if resource["default_key_flag"] == "1":
            return 0
        if resource["key_spec"] in notSupportList:
            return 0
        if resource["keystore_id"] != 0:
            return 0
        if resource["key_state"] not in {"2", "3", "4"}:
            return 0
        client = self.manager.get_client()
        request = EnableKeyRotationRequest()

        request.body = OperateKeyRequestBody(
            key_id=resource["key_id"],
            sequence=uuid.uuid4().hex
        )
        try:
            response = client.enable_key_rotation(request)
        except Exception as e:
            raise e

        return response


@Kms.action_registry.register("disable_key_rotation")
class disableRotationKey(HuaweiCloudBaseAction):
    """rotation kms key.

    :Example:

    .. code-block:: yaml

policies:
  - name: enable_key_rotation
    resource: huaweicloud.kms
    filters:
        - type: value
          key: key_rotation_enabled
          value: "False"
        - type: value
          key: domain_id
          value: "aaaaaaa"
    actions:
      - disable_key_rotation
    """

    schema = type_schema("disable_key_rotation")

    def perform_action(self, resource):

        notSupportList = {"RSA_2048", "RSA_3072", "RSA_4096", "EC_P256",
                          "EC_P384", "SM2", "ML_DSA_44",
                          "ML_DSA_65", "ML_DSA_87"}
        if resource["default_key_flag"] == "1":
            return 0
        if resource["key_spec"] in notSupportList:
            return 0
        if resource["keystore_id"] != 0:
            return 0
        if resource["key_state"] not in {"2", "3", "4"}:
            return 0
        client = self.manager.get_client()
        request = DisableKeyRotationRequest()
        request.body = OperateKeyRequestBody(
            key_id=resource["key_id"],
            sequence=uuid.uuid4().hex
        )
        try:
            response = client.disable_key_rotation(request)
        except Exception as e:
            raise e

        return response


@Kms.action_registry.register("enable_key")
class enableKey(HuaweiCloudBaseAction):
    """rotation kms key.

    :Example:

    .. code-block:: yaml

    policies:
      - name: enable_key
        resource: huaweicloud.kms
        filters:
          - type: value
            key: key_state
            value: "3"
        actions:
          - enable_key
    """

    schema = type_schema("enable_key")

    def perform_action(self, resource):
        client = self.manager.get_client()

        request = EnableKeyRequest()
        request.body = OperateKeyRequestBody(
            key_id=resource["key_id"],
            sequence=uuid.uuid4().hex
        )
        try:
            response = client.enable_key(request)
        except Exception as e:
            raise e

        return response


@Kms.action_registry.register("disable_key")
class disableKey(HuaweiCloudBaseAction):
    """rotation kms key.

    :Example:

    .. code-block:: yaml

    policies:
      - name: disable_key
        resource: huaweicloud.kms
        filters:
          - type: value
            key: key_state
            value: "2"
        actions:
          - disable_key
    """

    schema = type_schema("disable_key")

    def perform_action(self, resource):
        client = self.manager.get_client()
        request = DisableKeyRequest()
        request.body = OperateKeyRequestBody(
            key_id=resource["key_id"],
            sequence=uuid.uuid4().hex
        )
        try:
            response = client.disable_key(request)
        except Exception as e:
            raise e

        return response


@Kms.action_registry.register("create-key")
class createKey(HuaweiCloudBaseAction):
    """rotation kms key.

    :Example:

    .. code-block:: yaml

policies:
  - name: create-key
    resource: huaweicloud.kms
    actions:
      - type: create-key
        key_aliases: ["bbb"]
      - type: create-key
        obs_url: ""
    """

    schema = type_schema("create-key",
                         key_aliases={"type": "array"},
                         obs_url={"type": "string"})

    def process(self, resource):
        client = self.manager.get_client()
        key_aliases = self.data.get("key_aliases", [])
        request = ListKeysRequest()
        request.body = ListKeysRequestBody(
            key_spec="ALL",
            limit="1000")
        listKeyResponse = client.list_keys(request)
        arr = {"default"}
        for data in listKeyResponse.key_details:
            arr.add(data.key_alias)
        for alias in key_aliases:
            if alias not in arr:
                request = CreateKeyRequest()
                request.body = CreateKeyRequestBody(
                    key_alias=alias
                )
                try:
                    print(client.create_key(request))
                except Exception as e:
                    raise e

    def perform_action(self, resource):
        return super().perform_action(resource)


@Kms.filter_registry.register("all_keys_disable")
class instanceDisable(ValueFilter):
    '''
    policies:
      - name: all_keys_disable
        resource: huaweicloud.kms
        filters:
          - type: all_keys_disable
            key: "key_state"
            value: "2"
    '''
    schema = type_schema("all_keys_disable",
                         rinherit=ValueFilter.schema)
