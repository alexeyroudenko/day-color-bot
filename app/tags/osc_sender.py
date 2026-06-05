# from pythonosc.udp_client import SimpleUDPClient

# '''


# '''
# class OSCsender():
    
#     def __init__(self):
#         self.ip = "127.0.0.1"
#         self.port = 8888
#         self.client = SimpleUDPClient("127.0.0.1", self.port)

#     def on_event(self, args):
#         msg = args[0]
#         if msg == "tag":
#             tag_cmd = args[1]
#             tag_str = args[2]
#             #tag_id = args[3]
#             logging.info(f"send osc1 {msg}-{tag_cmd}-{tag_str}")
#             self.client.send_message("/" + msg, [tag_cmd, tag_str])            
        
#         if msg == "img":
#             cmd = args[1]
#             if len(args)>2:
#                 ... 
#                 # path = args[2]# logging.info(f"send osc2 {msg}-{cmd}-{path}")
#                 # import os
#                 # self.client.send_message("/" + msg, [cmd, os.path.abspath(path)])
#             else:
#                 logging.info(f"send osc3 {msg}-{cmd}")
                
#         if msg == "msg":
#             cmd = args[1]
#             msgg = args[2]
#             logging.info(f"send osc4 {msg}-{cmd}-{msg}")            
#             self.client.send_message("/" + msg, [cmd, msg])

#         if msg == "data":
#             cmd = args[1]
#             data = args[2]
#             logging.info(f"send osc5 data {data.dst} {data.tag_str}")            
#             self.client.send_message("/" + msg, [cmd, msg, data.dst, data.tag_str])

#         # if msg == "data":            
#         #     data = args[2]
#         #     logging.info(f"send osc {msg}-data")            
#         #     self.client.send_message("/" + msg, data)
