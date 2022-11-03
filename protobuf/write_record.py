from configuration.protobuf import data_pb2

def add_record(data):
    data.service = input("Enter service name ")
    data.version = input("Enter version ")
    data.is_used = int(input("if version is in use enter 2, if it is not enter 1 "))
    while True:
        service_key = input("Enter key or leave blank to finish ")
        service_value = input("Enter value or leave blank to finish ")
        if service_key == '':
            break
        keys = data.keys.add()
        keys.service_key = service_key
        keys.service_value = service_value

record = data_pb2.ConfigMessage()

add_record(record)

f = open('data.bin', 'wb')
f.write(record.SerializeToString())
f.close()
