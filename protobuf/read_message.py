import data_pb2


def read_file(data):
    print("Service: ", data.service)
    print("Version: ", data.version)
    print("Is_used: ", data.is_used)
    for i in range(len(data.keys)):
        print(data.keys[i])


record = data_pb2.ConfigMessage()

f = open("data.bin", "rb")
record.ParseFromString(f.read())
f.close()

read_file(record)
