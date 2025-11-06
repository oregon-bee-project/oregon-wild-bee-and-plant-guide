import zmq

PORT1 = 5556

def main():
    context1 = zmq.Context()
    socket1 = context1.socket(zmq.REQ)
    socket1.connect(f"tcp://localhost:{PORT1}")
    
    while(1):
        # do something
        coordinates = "44, -123" # must be in decimal degrees
        
        # send out microservice request
        request_json = {
            "request": "search_location",
            "arg1": coordinates,
            "error": False,
            "err_msg" : ""
        }
        
        socket1.send_json(request_json) 
        
        # receive microservice json
        response_json = socket1.recv_json()
        
        # check if error
        if response_json["error"]:
            print(f"ERROR - {response_json['err_msg']}")
        else:
            print(len(response_json["response"]))
        
        # run again or end
        i = input("e to end: ")
        if(i == "e"):
            break
        
    # terminate
    socket1.send_json({"request":"end"})
    socket1.recv_json()
    socket1.close()
    context1.term()
    

if __name__ ==  "__main__":
    main()