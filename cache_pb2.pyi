from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Key(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class Key_Value(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class PostReply(_message.Message):
    __slots__ = ["post_reply"]
    POST_REPLY_FIELD_NUMBER: _ClassVar[int]
    post_reply: bool
    def __init__(self, post_reply: bool = ...) -> None: ...

class GetReply(_message.Message):
    __slots__ = ["get_reply", "in_cache"]
    GET_REPLY_FIELD_NUMBER: _ClassVar[int]
    IN_CACHE_FIELD_NUMBER: _ClassVar[int]
    get_reply: str
    in_cache: bool
    def __init__(self, get_reply: _Optional[str] = ..., in_cache: bool = ...) -> None: ...

class DeleteReply(_message.Message):
    __slots__ = ["delete_reply"]
    DELETE_REPLY_FIELD_NUMBER: _ClassVar[int]
    delete_reply: bool
    def __init__(self, delete_reply: bool = ...) -> None: ...
