from concurrent import futures
from flask import Flask, request, jsonify, make_response
import json
import zlib
import sys
import logging
import grpc
import cache_pb2
import cache_pb2_grpc
from werkzeug.serving import make_server
import concurrent.futures

app = Flask(__name__)
DEFAULT_PORT = 9527
RPC_PORT = 5000


def crc16_hash(key):
    crc = zlib.crc32(key)
    return crc & 0xffff


def json_process(raw):
    data = json.loads(raw)
    return list(data)[0], list(data.values())[0]


cache = {}


@app.route('/<key>', methods=['GET'])
def get_op(key):
    target_port = crc16_hash(key.encode()) % cs_num + base_port
    rpc_port = target_port - base_port + RPC_PORT
    rpc_address = f"localhost:{rpc_port}"
    print(f"GET \"{key}\"")
    if target_port != port:
        print(f"MOVED To Server {target_port}")
        try:
            with grpc.insecure_channel(rpc_address) as channel:
                stub = cache_pb2_grpc.CacheStub(channel)
                response = stub.get(cache_pb2.Key(key=key))
                if response.in_cache:
                    return make_response(jsonify({key: response.get_reply}), 200)
                else:
                    return "", 404
        except Exception as e:
            # 处理异常情况
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        if key in cache:
            return jsonify({key: cache[key]})
        else:
            return "", 404


@app.route('/', methods=['POST'])
def post_op():
    print(request.data.decode('utf-8'))
    key, value = json_process(request.data.decode('utf-8'))
    print(key)
    print(f"POST \"{key}\": {value}")
    target_port = crc16_hash(key.encode()) % cs_num + base_port
    rpc_port = target_port - base_port + RPC_PORT
    rpc_address = f"localhost:{rpc_port}"
    if target_port != port:
        print(f"MOVED To Server {target_port}")
        try:
            with grpc.insecure_channel(rpc_address) as channel:
                stub = cache_pb2_grpc.CacheStub(channel)
                response = stub.post(cache_pb2.Key_Value(key=key, value=str(value)))
                if response.post_reply:
                    return " success"
                else:
                    return " fail"

        except Exception as e:
            # 处理异常情况
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        cache[key] = value
    return " success", 200


@app.route('/<key>', methods=['DELETE'])
def delete_op(key):
    target_port = crc16_hash(key.encode()) % cs_num + base_port
    rpc_port = target_port - base_port + RPC_PORT
    rpc_address = f"localhost:{rpc_port}"
    print(f"DELETE \"{key}\"")
    if target_port != port:
        print(f"MOVED To Server {target_port}")
        try:
            with grpc.insecure_channel(rpc_address) as channel:
                stub = cache_pb2_grpc.CacheStub(channel)
                response = stub.delete(cache_pb2.Key(key=key))
            if response.delete_reply:
                return jsonify(1)
            else:
                return jsonify(0)

        except Exception as e:
            # 处理异常情况
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        if key in cache:
            del cache[key]
            return "1", 200, {'Content-Type': 'application/json'}
        else:
            return "0", 200, {'Content-Type': 'application/json'}


# 接受rpc请求
class CacheServicerSelf(cache_pb2_grpc.CacheServicer):
    """Provides methods that implement functionality of route guide server."""

    def post(self, request, context, ):
        cache[request.key] = str(request.value)
        return cache_pb2.PostReply(post_reply=True)

    def get(self, request, context):
        if request.key in cache:
            return cache_pb2.GetReply(get_reply=str(cache[request.key]), in_cache=True)
        else:
            return cache_pb2.GetReply(get_reply=' ', in_cache=False)

    def delete(self, request, context):
        if request.key in cache:
            del cache[request.key]
            return cache_pb2.DeleteReply(delete_reply=True)
        else:
            return cache_pb2.DeleteReply(delete_reply=False)


def create_rpc_serve(r2_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cache_pb2_grpc.add_CacheServicer_to_server(
        CacheServicerSelf(), server
    )
    this_port = f"[::]:{r2_port}"
    server.add_insecure_port(this_port)
    server.start()
    server.wait_for_termination()


def http_launch(port1):
    app.config['JSON_AS_ASCII'] = False  # 解决中文乱码问题
    server = make_server('localhost', port1, app)
    server.serve_forever()


def grpc_launch(r1_port):
    logging.basicConfig()
    create_rpc_serve(r1_port)


if __name__ == '__main__':
    port = int(sys.argv[1])
    cs_num = int(sys.argv[2])
    base_port = DEFAULT_PORT  # http服务的端口
    r_port = port - DEFAULT_PORT + RPC_PORT  # rpc服务的端口
    with concurrent.futures.ThreadPoolExecutor() as executor:  # 多线程启动HTTP和rpc服务
        executor.submit(http_launch, port)
        executor.submit(grpc_launch, r_port)
