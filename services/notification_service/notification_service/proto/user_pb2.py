# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/user.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/user.proto\"\x8d\x01\n\x0bUserProfile\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\x05\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\r\n\x05\x65mail\x18\x04 \x01(\t\x12\r\n\x05phone\x18\x05 \x01(\t\x12\x18\n\x10shipping_address\x18\x06 \x01(\t\x12\x15\n\rpayment_token\x18\x07 \x01(\t\"\x8a\x01\n\x0bUserMessage\x12\x1f\n\x0cmessage_type\x18\x01 \x01(\x0e\x32\t.MessageT\x12\'\n\x0cprofile_data\x18\x02 \x01(\x0b\x32\x0c.UserProfileH\x00\x88\x01\x01\x12\x14\n\x07user_id\x18\x03 \x01(\x05H\x01\x88\x01\x01\x42\x0f\n\r_profile_dataB\n\n\x08_user_id*8\n\x08MessageT\x12\x0c\n\x08\x61\x64\x64_user\x10\x00\x12\r\n\tedit_user\x10\x01\x12\x0f\n\x0b\x64\x65lete_user\x10\x02\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.user_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGET']._serialized_start=305
  _globals['_MESSAGET']._serialized_end=361
  _globals['_USERPROFILE']._serialized_start=21
  _globals['_USERPROFILE']._serialized_end=162
  _globals['_USERMESSAGE']._serialized_start=165
  _globals['_USERMESSAGE']._serialized_end=303
# @@protoc_insertion_point(module_scope)
